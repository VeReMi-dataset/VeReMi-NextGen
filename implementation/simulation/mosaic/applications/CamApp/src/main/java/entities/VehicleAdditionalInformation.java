package entities;

import org.eclipse.mosaic.lib.enums.SpeedMode;
import org.eclipse.mosaic.lib.geo.CartesianPoint;

import java.io.Serializable;

public class VehicleAdditionalInformation implements Serializable {
    public double speedNoise;
    public double headingNoise;
    public CartesianPoint positionNoise;
    public double accelerationNoise;
    public long alias;
    public SpeedMode speedMode;
    public CartesianPoint positionCartesian;
}
