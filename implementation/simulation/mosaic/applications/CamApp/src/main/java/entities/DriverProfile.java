package entities;

import org.eclipse.mosaic.lib.enums.LaneChangeMode;
import org.eclipse.mosaic.lib.enums.SpeedMode;

public enum DriverProfile {

    AGGRESSIVE(0.5, 3.1, 5.0, 1.1, 0.5, 2.0, LaneChangeMode.AGGRESSIVE, SpeedMode.AGGRESSIVE),
    NORMAL(1.0, 2.6, 4.5, 1.0, 0.5, 2.5, LaneChangeMode.DEFAULT, SpeedMode.NORMAL),
    PASSIVE(1.5, 2.1, 4.0, 0.9, 0.5, 3,LaneChangeMode.CAUTIOUS, SpeedMode.CAUTIOUS);

    final double tau;
    final double accel;
    final double decel;
    final double speedFactor;
    final double sigma;
    final double minGap;
    final LaneChangeMode laneChangeMode;
    final SpeedMode speedMode;

    DriverProfile(double tau, double accel, double decel,
                  double speedFactor, double sigma, double minGap,
                  LaneChangeMode laneChangeMode, SpeedMode speedMode) {
        this.tau = tau;
        this.accel = accel;
        this.decel = decel;
        this.speedFactor = speedFactor;
        this.sigma = sigma;
        this.minGap = minGap;
        this.laneChangeMode = laneChangeMode;
        this.speedMode = speedMode;
    }

    public double getTau() { return tau; }
    public double getAccel() { return accel; }
    public double getDecel() { return decel; }
    public double getSpeedFactor() { return speedFactor; }
    public double getSigma() { return sigma; }
    public double getMinGap() { return minGap; }
    public LaneChangeMode getLaneChangeMode() { return laneChangeMode; }
    public SpeedMode getSpeedMode() { return speedMode; }
}
