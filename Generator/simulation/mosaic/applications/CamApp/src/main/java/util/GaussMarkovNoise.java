package util;

import java.util.Random;

public class GaussMarkovNoise {
    private final double alpha;
    private final double sigma;
    private double currentValue;
    private final Random random;

    /**
     * @param alpha        Korrelation (typischerweise alpha = exp(-dt/τ))
     * @param sigma        Standardabweichung des Rauschens
     * @param initialValue Startwert (z.B. 0.0)
     */
    public GaussMarkovNoise(double alpha, double sigma, double initialValue) {
        this.alpha = alpha;
        this.sigma = sigma;
        this.currentValue = initialValue;
        this.random = new Random();
    }

    /**
     * Berechnet den nächsten Wert im Gauss-Markov-Prozess.
     *
     * @return Neuer Prozesswert.
     */
    public double nextValue() {
        double noise = Math.abs(random.nextGaussian()) * Math.sqrt(1 - alpha * alpha) * sigma;
        currentValue = alpha * currentValue + noise;
        return currentValue;
    }

}
