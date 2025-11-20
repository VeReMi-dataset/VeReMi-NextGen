package entities;

import com.google.gson.annotations.JsonAdapter;
import org.eclipse.mosaic.lib.util.gson.DataFieldAdapter;
import org.eclipse.mosaic.lib.util.gson.TimeFieldAdapter;
import org.eclipse.mosaic.lib.util.gson.UnitFieldAdapter;


public class ConfigSettings {
    @JsonAdapter(DataFieldAdapter.Size.class)
    public long minimalPayloadLength = 200L;

    @JsonAdapter(TimeFieldAdapter.NanoSeconds.class)
    public long maxStartOffset = 1_000_000_000L; // 1s in nanoseconds

    @JsonAdapter(TimeFieldAdapter.NanoSeconds.class)
    public Long minInterval = 500_000_000L; // 500ms in nanoseconds

    @JsonAdapter(TimeFieldAdapter.NanoSeconds.class)
    public Long maxInterval = 1_000_000_000L; // 1s in nanoseconds

    @JsonAdapter(UnitFieldAdapter.DistanceMetersQuiet.class)
    public Double positionChange = 4.0;

    public Double headingChange = 4.0;

    @JsonAdapter(UnitFieldAdapter.SpeedMSQuiet.class)
    public Double velocityChange = 0.5;

    public String jsonPath = "C:/simulation/mosaic/JSON/";

    public SimulationTime simulationTime = new SimulationTime();

    public SimulationArea simulationArea = new SimulationArea();

    public boolean enableDriverProfiles = false;

    public ConfigSettings() {
    }

    public static class SimulationTime {
        @JsonAdapter(TimeFieldAdapter.LegacySeconds.class)
        public long start = 0;
        @JsonAdapter(TimeFieldAdapter.LegacySeconds.class)
        public long end = 86400;
    }

    public static class SimulationArea {
        public double minX = 48.724467;
        public double minY = 11.353690;
        public double maxX = 48.801995;
        public double maxY = 11.498488;
    }
}

