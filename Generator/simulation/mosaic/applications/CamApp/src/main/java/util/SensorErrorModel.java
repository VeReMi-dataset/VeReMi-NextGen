package util;

import org.eclipse.mosaic.lib.geo.CartesianPoint;
import org.eclipse.mosaic.lib.geo.MutableCartesianPoint;
import org.eclipse.mosaic.lib.geo.MutableGeoPoint;

import java.util.Random;

public class SensorErrorModel {

    private static final Random random = new Random();
    private static final double EARTH_RADIUS = 6378137.0;

    private final double initialXPositionError;
    private final double initialYPositionError;
    private final double initialSpeedError;
    private final double initialHeadingError;

    private double previousSpeedError;
    private double previousXPositionError;
    private double previousYPositionError;
    private double correctedSpeed;
    private double currentSpeedError;
    private long lastMessage;


    public SensorErrorModel() {
        this.initialXPositionError = uniform(-5.0, 5.0);
        this.initialYPositionError = uniform(-5.0, 5.0);
        this.initialSpeedError = gaussian(0.0, 0.00016);
        this.previousSpeedError = 0;
        this.currentSpeedError = 0;
        this.previousXPositionError = initialXPositionError;
        this.previousYPositionError = initialYPositionError;
        this.initialHeadingError = uniform(-20.0, 20.0);
        this.lastMessage = 0;
    }

    public Pair<MutableCartesianPoint, MutableCartesianPoint> addPositionNoise(CartesianPoint truePosition) {
        double muX = (initialXPositionError + previousXPositionError) / 2.0;
        double muY = (initialYPositionError + previousYPositionError) / 2.0;
        double sigmaX = 0.03 * Math.abs(initialXPositionError);
        double sigmaY = 0.03 * Math.abs(initialYPositionError);
        double noiseX = gaussian(muX, sigmaX);
        double noiseY = gaussian(muY, sigmaY);
        previousXPositionError = noiseX;
        previousYPositionError = noiseY;

        return new Pair(new MutableCartesianPoint(truePosition.getX() + noiseX, truePosition.getY() + noiseY, 0), new MutableCartesianPoint(noiseX, noiseY,0));
    }

    public Pair<Double, Double> addSpeedNoise(double trueVelocity) {
        correctedSpeed = trueVelocity * (1.0 + initialSpeedError);
        currentSpeedError = trueVelocity - correctedSpeed;
        return new Pair(correctedSpeed, currentSpeedError);
    }

    public Pair<Double, Double> addAccelerationNoise(double acceleration, long currentTime) {
        double deltaT = (currentTime - lastMessage) / 1_000_000_000.0;
        double error = (currentSpeedError - previousSpeedError) / deltaT;
        double accError = acceleration + error;
        lastMessage = currentTime;
        previousSpeedError = currentSpeedError;
        return new Pair(accError,error);
    }

    public Pair<Double, Double> addHeadingNoise(double trueHeading, double velocity) {
        double decay = Math.exp(-0.1 * velocity);
        double currentError = initialHeadingError * decay;
        double noisyHeading = trueHeading + currentError;

        if (noisyHeading >= 360) {
            noisyHeading -= 360;
        } else if (noisyHeading < 0) {
            noisyHeading += 360;
        }
        return new Pair(noisyHeading, currentError);
    }

    private static double uniform(double min, double max) {
        return min + (max - min) * random.nextDouble();
    }

    private static double gaussian(double mean, double stddev) {
        return random.nextGaussian(mean, stddev);
    }
}
