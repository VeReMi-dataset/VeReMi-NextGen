/*
 * Copyright (c) 2020 Fraunhofer FOKUS and others. All rights reserved.
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 * Contact: mosaic@fokus.fraunhofer.de
 */

package etsi;

import entities.DriverProfile;
import entities.VehicleAdditionalInformation;
import org.eclipse.mosaic.fed.application.ambassador.simulation.communication.CamBuilder;
import org.eclipse.mosaic.fed.application.ambassador.simulation.communication.ReceivedAcknowledgement;
import org.eclipse.mosaic.fed.application.ambassador.simulation.communication.ReceivedV2xMessage;
import org.eclipse.mosaic.fed.application.app.api.os.VehicleOperatingSystem;
import org.eclipse.mosaic.interactions.communication.V2xMessageTransmission;
import org.eclipse.mosaic.lib.geo.CartesianPoint;
import org.eclipse.mosaic.lib.geo.MutableCartesianPoint;
import org.eclipse.mosaic.lib.objects.v2x.V2xMessage;
import org.eclipse.mosaic.lib.objects.v2x.etsi.Cam;
import org.eclipse.mosaic.lib.objects.v2x.etsi.cam.VehicleAwarenessData;
import org.eclipse.mosaic.lib.objects.vehicle.VehicleData;
import util.JSONParser;
import util.Pair;
import util.SensorErrorModel;
import util.SerializationUtils;

import java.io.IOException;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.Objects;
import java.util.Random;

/**
 * ETSI conform application for vehicles.
 */
public class VehicleCamSendingApp extends AbstractCamSendingApp<VehicleOperatingSystem> {

    JSONParser jsonParser = new JSONParser();
    SerializationUtils serializationUtils = new SerializationUtils();
    SensorErrorModel sensorErrorModel = new SensorErrorModel();

    private Data data = new Data();
    private double distanceDrivenSinceLastChange = 0;
    private boolean firstChange = true;
    private boolean randomDistanceSet = false;
    private double randomDistance = 800;
    private boolean randomTimeSet = false;
    private double randomTime;
    private CartesianPoint lastPosition;
    private LocalDateTime initialTime = LocalDateTime.now();
    private DriverProfile driverProfile;

    private Pair<MutableCartesianPoint, MutableCartesianPoint> postProcessingPoint;
    private Pair<Double, Double> postProcessingSpeed;
    private Pair<Double, Double> postProcessingAcceleration;
    private Pair<Double, Double> postProcessingHeading;

    @Override
    public void onStartup() {
        getLog().debugSimTime(this, "Initialize application");
        activateCommunicationModule();

        if (getConfiguration().enableDriverProfiles) {
            Random rand = new Random();
            double randomValue = rand.nextDouble();

            if (randomValue < 0.10) {
                driverProfile = DriverProfile.AGGRESSIVE;
            } else if (randomValue < 0.90) {
                driverProfile = DriverProfile.NORMAL;
            } else{
                driverProfile = DriverProfile.PASSIVE;
            }

            applyDriverProfile();
        }

        firstSample();
    }

    @Override
    public Data generateEtsiData() {
        VehicleData vehicleData = getOperatingSystem().getVehicleData();
        if (vehicleData == null) {
            return null;
        }
        final Data myData = new Data();
        lastPosition = getOperatingSystem().getVehicleData().getProjectedPosition();
        getPostProcessingValue(vehicleData);
        myData.time = getOperatingSystem().getSimulationTime(); // getTime oder getSimulationTime?
        myData.projectedPosition = vehicleData.getProjectedPosition();
        myData.heading = postProcessingHeading.getFirst();
        myData.position = vehicleData.getPosition();
        myData.velocity = postProcessingSpeed.getFirst();
        myData.acceleration = postProcessingAcceleration.getFirst();
        myData.positionNoise = postProcessingPoint.getSecond();
        myData.headingNoise = postProcessingHeading.getSecond();
        myData.speedNoise = postProcessingSpeed.getSecond();
        myData.accelerationNoise = postProcessingAcceleration.getSecond();
        myData.alias = data.alias;
        myData.speedMode = getOperatingSystem().getVehicleParameters().getSpeedMode();
        myData.cartesianPoint = postProcessingPoint.getFirst();
        data = myData;
        return myData;
    }

    public Data generateReceiverData() {
        VehicleData vehicleData = getOperatingSystem().getVehicleData();
        if (vehicleData == null) {
            return null;
        }
        final Data myData = new Data();
        lastPosition = getOperatingSystem().getVehicleData().getProjectedPosition();
        getPostProcessingValue(vehicleData);
        myData.heading = postProcessingHeading.getFirst();
        myData.position = vehicleData.getPosition();
        myData.velocity = postProcessingSpeed.getFirst();
        myData.acceleration = postProcessingAcceleration.getFirst();
        myData.positionNoise = postProcessingPoint.getSecond();
        myData.headingNoise = postProcessingHeading.getSecond();
        myData.speedNoise = postProcessingSpeed.getSecond();
        myData.accelerationNoise = postProcessingAcceleration.getSecond();
        myData.speedMode = getOperatingSystem().getVehicleParameters().getSpeedMode();
        myData.cartesianPoint = postProcessingPoint.getFirst();
        return myData;
    }

    @Override
    public void onAcknowledgementReceived(ReceivedAcknowledgement receivedAcknowledgement) {

    }

    @Override
    public void onCamBuilding(CamBuilder camBuilder) {
        VehicleAdditionalInformation vehicleAdditionalInformation = new VehicleAdditionalInformation();
        vehicleAdditionalInformation.speedNoise = data.speedNoise;
        vehicleAdditionalInformation.positionNoise = data.positionNoise;
        vehicleAdditionalInformation.headingNoise = data.headingNoise;
        vehicleAdditionalInformation.accelerationNoise = data.accelerationNoise;
        vehicleAdditionalInformation.alias = data.alias;
        vehicleAdditionalInformation.speedMode = data.speedMode;
        vehicleAdditionalInformation.positionCartesian = data.cartesianPoint;

        try {
            camBuilder.position(data.position).
                    awarenessData(new VehicleAwarenessData(
                            getOperatingSystem().getInitialVehicleType().getVehicleClass(),
                            data.velocity,
                            data.heading,
                            0,
                            0,
                            getOperatingSystem().getVehicleData().getDriveDirection(),
                            0,
                            getOs().getVehicleData().getLongitudinalAcceleration()
                    ))
                    .userTaggedValue(serializationUtils.toBytes(vehicleAdditionalInformation))
                    .create(data.time, getOs().getId());
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public void onMessageTransmitted(V2xMessageTransmission v2xMessageTransmission) {
        distanceDrivenSinceLastChange += this.data.projectedPosition.distanceTo(lastPosition);
        LocalDateTime now = LocalDateTime.now();
        if (firstChange) {
            if (!randomDistanceSet) {
                randomDistance =  800 + (1500 - 800) * Math.random();
                randomDistanceSet = true;
            }
            if (distanceDrivenSinceLastChange > randomDistance) {
                data.alias = (long) ((Math.random() * 9_000_000_000L) + 1_000_000_000L);
                distanceDrivenSinceLastChange = 0;
                firstChange = false;
            }
        } else {
            if (distanceDrivenSinceLastChange > randomDistance) {
                if (!randomTimeSet) {
                    randomTime =  120000 + (360000 - 120000) * Math.random();
                    randomTimeSet = true;
                }
                if (Duration.between(initialTime, now).toMillis() > randomTime) {
                    data.alias = (long) ((Math.random() * 9_000_000_000L) + 1_000_000_000L);
                    distanceDrivenSinceLastChange = 0;
                    initialTime = now;
                    randomTimeSet = false;
                }
            }
        }
    }

    private void getPostProcessingValue(VehicleData vehicleData) {
        postProcessingPoint = sensorErrorModel.addPositionNoise(vehicleData.getProjectedPosition());
        postProcessingSpeed = sensorErrorModel.addSpeedNoise(vehicleData.getSpeed());
        postProcessingAcceleration = sensorErrorModel.addAccelerationNoise(vehicleData.getLongitudinalAcceleration(), getOperatingSystem().getSimulationTime());
        postProcessingHeading = sensorErrorModel.addHeadingNoise(vehicleData.getHeading(), vehicleData.getSpeed());
    }

    @Override
    public void onMessageReceived(ReceivedV2xMessage receivedV2xMessage) {
        getLog().infoSimTime(this, "Received V2X Message:", receivedV2xMessage);
        try {
            if(isInSimulationArea()) {
                jsonParser.parseAndWriteJson(createJSONString(receivedV2xMessage), getConfiguration().jsonPath + getOs().getId() + ".json");
            }
        } catch (Exception e) {
            getLog().infoSimTime(this, "Error while parsing json");
        }
    }

    public String createJSONString(ReceivedV2xMessage receivedV2xMessage) throws IOException, ClassNotFoundException {
        V2xMessage v2xMessage = receivedV2xMessage.getMessage();
        Data receiverData = generateReceiverData();
        if (v2xMessage instanceof Cam cam) {
            VehicleAdditionalInformation vehicleAdditionalInformation = serializationUtils.fromBytes(Objects.requireNonNull(cam.getUserTaggedValue()));
            if (cam.getAwarenessData() instanceof VehicleAwarenessData vehicleAwarenessData) {

                String senderJson = "{"
                        + "\"pos\":\"" + vehicleAdditionalInformation.positionCartesian.getX() + ","
                        + vehicleAdditionalInformation.positionCartesian.getY() + ","
                        + vehicleAdditionalInformation.positionCartesian.getZ() + "\","
                        + "\"pos_noise\":\"" + vehicleAdditionalInformation.positionNoise.getX() + ","
                        + vehicleAdditionalInformation.positionNoise.getY() + ","
                        + vehicleAdditionalInformation.positionNoise.getZ() + "\","
                        + "\"spd\":\"" + vehicleAwarenessData.getSpeed() + "\","
                        + "\"spd_noise\":\"" + vehicleAdditionalInformation.speedNoise + "\","
                        + "\"acl\":\"" + vehicleAwarenessData.getLongitudinalAcceleration() + "\","
                        + "\"acl_noise\":\"" + vehicleAdditionalInformation.accelerationNoise + "\","
                        + "\"hed\":\"" + vehicleAwarenessData.getHeading() + "\","
                        + "\"hed_noise\":\"" + vehicleAdditionalInformation.headingNoise + "\","
                        + "\"driversProfile\":\"" + vehicleAdditionalInformation.speedMode + "\""
                        + "}";

                String receiverJSON = "{"
                        + "\"pos\":\"" + receiverData.cartesianPoint.getX() + ","
                        + receiverData.cartesianPoint.getY() + ","
                        + receiverData.cartesianPoint.getZ() + "\","
                        + "\"pos_noise\":\"" + receiverData.positionNoise.getX() + ","
                        + receiverData.positionNoise.getY() + ","
                        + receiverData.positionNoise.getZ() + "\","
                        + "\"spd\":\"" + receiverData.velocity + "\","
                        + "\"spd_noise\":\"" + receiverData.speedNoise + "\","
                        + "\"acl\":\"" + receiverData.acceleration + "\","
                        + "\"acl_noise\":\"" + receiverData.accelerationNoise + "\","
                        + "\"hed\":\"" + receiverData.heading + "\","
                        + "\"hed_noise\":\"" + receiverData.headingNoise + "\","
                        + "\"driversProfile\":\"" + receiverData.speedMode + "\""
                        + "}";

                return "{"
                        + "\"rcvTime\":\"" + receivedV2xMessage.getReceiverInformation().getReceiveTime() + "\","
                        + "\"sendTime\":\"" + cam.getGenerationTime() + "\","
                        + "\"sender_id\":\"" + cam.getRouting().getSource().getSourceName() + "\","
                        + "\"sender_alias\":\"" + vehicleAdditionalInformation.alias + "\","
                        + "\"messageID\":\"" + cam.getId() + "\","
                        + "\"receiver\":" + receiverJSON + ","
                        + "\"sender\":" + senderJson
                        + "}";
            }
            return "{\"rcvTime\":\"" + LocalDateTime.now() + "\"," +
                    "\"sendTime\":\"" + cam.getGenerationTime() + "\"," +
                    "\"sender\":\"" + cam.getRouting().getSource().getSourceName() + "\"," +
                    "\"messageID\":\"" + cam.getId() + "\"}";
        }
        return "{\"rcvTime\":\"" + LocalDateTime.now() + "\"}";
    }

    public boolean isInSimulationArea() {
        if(getOperatingSystem().getVehicleData() != null && getOperatingSystem().getRoadPosition() != null) {
            double x = getOperatingSystem().getVehicleData().getPosition().getLatitude();
            double y = getOperatingSystem().getVehicleData().getPosition().getLongitude();
            return x >= getConfiguration().simulationArea.minX && x <= getConfiguration().simulationArea.maxX &&
                    y >= getConfiguration().simulationArea.minY && y <= getConfiguration().simulationArea.maxY;
        }
        return false;
    }

    public boolean isInSimulationTime() {
        return (getOperatingSystem().getSimulationTime()/1000000000 > getConfiguration().simulationTime.start
                && getOperatingSystem().getSimulationTime()/1000000000 < getConfiguration().simulationTime.end);
    }

    private void applyDriverProfile() {
        getOs().requestVehicleParametersUpdate()
                .changeReactionTime(driverProfile.getTau())
                .changeMaxAcceleration(driverProfile.getAccel())
                .changeMaxDeceleration(driverProfile.getDecel())
                .changeSpeedFactor(driverProfile.getSpeedFactor())
                .changeImperfection(driverProfile.getSigma())
                .changeMinimumGap(driverProfile.getMinGap())
                .changeLaneChangeMode(driverProfile.getLaneChangeMode())
                .changeSpeedMode(driverProfile.getSpeedMode())
                .apply();
    }
}
