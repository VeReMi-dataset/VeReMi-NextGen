# Results

Documentation of all metrics used and results regarding the creation and evaluation of the VeReMi NextGen Dataset.

## Metrics

### Definition of classification

- TP (True Positive): A message was predicted as an attacker and is indeed an attacker.
- TN (True Negative): A message was not predicted as an attacker and is indeed not an attacker.
- FP (False Positive): A message was predicted as an attacker, but is not an attacker.
- FN (False Negative): A message was not predicted as an attacker, although it is an attacker.

### Confusion Matrix
|                     |                  | **Actual Class** |                  |
| ------------------- | ---------------- | ---------------- | ---------------- |
|                     |                  | **Attacker**     | **Non-Attacker** |
| **Predicted Class** | **Attacker**     | TP               | FP               |
|                     | **Non-Attacker** | FN               | TN               |

### Evaluation Metrics

$$
\text{Precision} = \frac{TP}{TP + FP}
$$

$$
\text{Recall} = \frac{TP}{TP + FN}
$$

$$
\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}
$$

$$
\text{F1} = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}
{\text{Precision} + \text{Recall}}
$$

## Driver Profiles
The following tables show the average values for the different driver profiles generated in the four simulations.
They provide insight how the profiles are actually distributed and how they differ.

### Urban - Low density
| **Profile** | **Ø Speed**       | **Ø Accel.**     | **Distribution** |
|-------------|-------------------|------------------|------------------|
| Normal      | 12.06 (σ = 2.81)  | 0.00 (σ = 0.86)  | 80.39 %          |
| Cautious    | 8.41 (σ = 4.99)   | 0.00 (σ = 0.96)  | 12.46 %          |
| Aggressive  | 23.10 (σ = 15.39) | -0.09 (σ = 1.94) | 7.15 %           |


### Urban - high density
| **Profile** | **Ø Speed**       | **Ø Accel.**     | **Distribution** |
|-------------|-------------------|------------------|------------------|
| Normal      | 7.09 (σ = 5.82)   | -0.01 (σ = 1.00) | 82.69 %          |
| Cautious    | 6.53 (σ = 5.42)   | 0.00 (σ = 0.88)  | 10.33 %          |
| Aggressive  | 12.35 (σ = 11.06) | -0.14 (σ = 1.99) | 6.98 %           |


### Highway - Low density
| **Profile** | **Ø Speed**       | **Ø Accel.**     | **Distribution** |
|-------------|-------------------|------------------|------------------|
| Normal      | 23.63 (σ = 16.87) | 0.05 (σ = 1.25)  | 77.38 %          |
| Cautious    | 15.36 (σ = 17.13) | 0.07 (σ = 1.12)  | 15.50 %          |
| Aggressive  | 42.79 (σ = 16.15) | -0.14 (σ = 1.92) | 6.12 %           |


### Highway - high density
| **Profile** | **Ø Speed**       | **Ø Accel.**     | **Distribution** |
|-------------|-------------------|------------------|------------------|
| Normal      | 10.47 (σ = 17.19) | 0.03 (σ = 1.09)  | 82.10 %          |
| Cautious    | 11.31 (σ = 17.56) | 0.08 (σ = 1.00)  | 9.25 %           |
| Aggressive  | 17.40 (σ = 19.70) | -1.19 (σ = 2.38) | 8.65 %           |


## Parameter Optimization

The following values were used to run the given MBD systems and assess the values provided later.

| **Parameter** | **Urban 2AM** | **Urban 7AM** | **Highway 2AM** | **Highway 7AM** |
|---------------|---------------|---------------|-----------------|-----------------|
| MPR           | 336.568       | 328.469       | 309.270         | 321.918         |
| MPDN          | -1.793        | -2.144        | -2.742          | -3.813          |
| MPS           | 57.338        | 30.007        | 56.064          | 55.620          |
| MPA           | 3.121         | 3.120         | 3.138           | 3.429           |
| MPD           | 4.569         | 5.091         | 6.131           | 4.849           |
| MHC           | 71.385        | 111.710       | 115.995         | 129.867         |
| MDI           | 4.697         | 1.242         | 3.757           | 4.906           |
| MTD           | 3.666         | 3.618         | 1.538           | 3.539           |
| PHT           | 1.415         | 4.384         | 1.837           | 3.232           |
| MMRU          | 1.118         | 1.182         | 1.168           | 1.123           |
| MMRD          | 2.584         | 2.137         | 2.902           | 1.438           |
| MNRS          | 0.051         | 0.000         | 0.490           | 0.265           |

## MBD Results of VeReMi NextGen
The following tables show the values assessed by using the newly generated dataset with the proposed MBD system 

### Urban - low density
| **Attack Type**             | **TP** | **TN** | **FP** | **FN** |
|-----------------------------|-------:|-------:|-------:|-------:|
| Time Delay Attack           |   2357 | 334278 |   8388 |  61778 |
| Constant Position Offset    |  64648 | 318680 |   7736 |  15737 |
| Random Position Offset      |  76171 | 321065 |   8527 |   1038 |
| Position Mirroring          |   9133 | 321186 |   7972 |  68510 |
| Constant Speed Offset       |  40817 | 319536 |   8003 |  38445 |
| Random Speed Offset         |  59622 | 318908 |   7186 |  21085 |
| Zero Speed Report           |  72573 | 319494 |   9339 |   5395 |
| Sudden Stop                 |    796 | 354318 |   9917 |  41770 |
| Sudden Constant Speed       |   3348 | 386606 |  13923 |   2924 |
| Reversed Heading            |  37642 | 317618 |   8382 |  43159 |
| Feigned Braking             |    563 | 366037 |  10084 |  30117 |
| Acceleration Multiplication |   1082 | 365405 |   9565 |  30749 |
| DoS Attack                  |  57845 | 315392 |   8759 | 203227 |
| Traffic Congestion Sybil    |  56132 | 396128 |  10673 | 309223 |
| Data Replay                 |  13246 | 323114 |   9026 |  61415 |

| **Attack Type**             | **Accuracy** | **Precision** | **Recall** | **F1 Score** |
|-----------------------------|-------------:|--------------:|-----------:|-------------:|
| Time Delay Attack           |        0.827 |         0.219 |      0.036 |        0.062 |
| Constant Position Offset    |        0.942 |         0.893 |      0.804 |        0.846 |
| Random Position Offset      |        0.976 |         0.899 |      0.986 |        0.940 |
| Position Mirroring          |        0.811 |         0.533 |      0.117 |        0.192 |
| Constant Speed Offset       |        0.885 |         0.836 |      0.514 |        0.637 |
| Random Speed Offset         |        0.930 |         0.892 |      0.738 |        0.808 |
| Zero Speed Report           |        0.963 |         0.885 |      0.930 |        0.907 |
| Sudden Stop                 |        0.872 |         0.074 |      0.018 |        0.029 |
| Sudden Constant Speed       |        0.958 |         0.193 |      0.533 |        0.284 |
| Reversed Heading            |        0.873 |         0.817 |      0.465 |        0.593 |
| Feigned Braking             |        0.901 |         0.052 |      0.018 |        0.027 |
| Acceleration Multiplication |        0.900 |         0.101 |      0.033 |        0.050 |
| DoS Attack                  |        0.637 |         0.868 |      0.221 |        0.353 |
| Traffic Congestion Sybil    |        0.585 |         0.840 |      0.153 |        0.259 |
| Data Replay                 |        0.826 |         0.594 |      0.177 |        0.273 |

### Urban - high density
| **Attack Type**             | **TP** |  **TN** | **FP** |  **FN** |
|-----------------------------|-------:|--------:|-------:|--------:|
| Time Delay Attack           |  13336 | 3556187 |  55992 | 1028416 |
| Constant Position Offset    | 346932 | 3762791 |  54839 |  489369 |
| Random Position Offset      | 853061 | 3732815 |  55077 |   12978 |
| Position Mirroring          |  53933 | 3763310 |  56755 |  779933 |
| Constant Speed Offset       | 241679 | 3839755 |  51112 |  521385 |
| Random Speed Offset         | 715831 | 3503563 |  49847 |  384690 |
| Zero Speed Report           | 334118 | 4202516 |  57356 |   59941 |
| Sudden Stop                 |   3842 | 4245026 |  62018 |  343045 |
| Sudden Constant Speed       |  61037 | 4426872 | 130627 |   35395 |
| Reversed Heading            | 190708 | 4185133 |  57059 |  221031 |
| Feigned Braking             |   3834 | 4408818 |  65630 |  175649 |
| Acceleration Multiplication |   9254 | 4363508 |  60210 |  220959 |
| DoS Attack                  | 389371 | 3432083 |  60557 | 2948800 |
| Traffic Congestion Sybil    | 338156 | 4581769 |  72162 | 4257837 |
| Data Replay                 | 240059 | 3491410 | 149464 |  772998 |

| **Attack Type**             | **Accuracy** | **Precision** | **Recall** | **F1 Score** |
|-----------------------------|-------------:|--------------:|-----------:|-------------:|
| Time Delay Attack           |        0.767 |         0.192 |      0.013 |        0.024 |
| Constant Position Offset    |        0.883 |         0.863 |      0.414 |        0.560 |
| Random Position Offset      |        0.985 |         0.939 |      0.985 |        0.962 |
| Position Mirroring          |        0.820 |         0.487 |      0.065 |        0.114 |
| Constant Speed Offset       |        0.877 |         0.825 |      0.317 |        0.458 |
| Random Speed Offset         |        0.906 |         0.934 |      0.650 |        0.767 |
| Zero Speed Report           |        0.975 |         0.853 |      0.848 |        0.851 |
| Sudden Stop                 |        0.912 |         0.058 |      0.011 |        0.018 |
| Sudden Constant Speed       |        0.964 |         0.318 |      0.633 |        0.424 |
| Reversed Heading            |        0.940 |         0.770 |      0.463 |        0.578 |
| Feigned Braking             |        0.948 |         0.055 |      0.021 |        0.031 |
| Acceleration Multiplication |        0.940 |         0.133 |      0.040 |        0.062 |
| DoS Attack                  |        0.559 |         0.865 |      0.117 |        0.206 |
| Traffic Congestion Sybil    |        0.532 |         0.824 |      0.074 |        0.135 |
| Data Replay                 |        0.802 |         0.616 |      0.237 |        0.342 |

### Highway - low density
| **Attack Type**             | **TP** | **TN** | **FP** | **FN** |
|-----------------------------|-------:|-------:|-------:|-------:|
| Time Delay Attack           |    874 |  31257 |   4322 |   7806 |
| Constant Position Offset    |   6113 |  31444 |   4105 |   2597 |
| Random Position Offset      |   8052 |  31923 |   4056 |    228 |
| Position Mirroring          |   1426 |  30351 |   4290 |   8192 |
| Constant Speed Offset       |   4866 |  31256 |   4103 |   4034 |
| Random Speed Offset         |   6160 |  31899 |   3966 |   2234 |
| Zero Speed Report           |   7806 |  31794 |   4055 |    604 |
| Sudden Stop                 |    851 |  35502 |   4817 |   3089 |
| Sudden Constant Speed       |   1269 |  36939 |   5749 |    302 |
| Reversed Heading            |   4198 |  31964 |   4027 |   4070 |
| Feigned Braking             |    289 |  35856 |   4907 |   3207 |
| Acceleration Multiplication |    538 |  35494 |   4658 |   3569 |
| DoS Attack                  |   9707 |  31757 |   4309 |  14945 |
| Traffic Congestion Sybil    |  10041 |  39063 |   5196 |  29594 |
| Data Replay                 |   2142 |  31048 |   4468 |   6601 |

| **Attack Type**             | **Accuracy** | **Precision** | **Recall** | **F1 Score** |
|-----------------------------|-------------:|--------------:|-----------:|-------------:|
| Time Delay Attack           |        0.726 |         0.168 |      0.101 |        0.126 |
| Constant Position Offset    |        0.849 |         0.598 |      0.702 |        0.646 |
| Random Position Offset      |        0.903 |         0.665 |      0.972 |        0.790 |
| Position Mirroring          |        0.718 |         0.249 |      0.148 |        0.186 |
| Constant Speed Offset       |        0.816 |         0.543 |      0.547 |        0.545 |
| Random Speed Offset         |        0.860 |         0.608 |      0.734 |        0.665 |
| Zero Speed Report           |        0.895 |         0.658 |      0.928 |        0.770 |
| Sudden Stop                 |        0.821 |         0.150 |      0.216 |        0.177 |
| Sudden Constant Speed       |        0.863 |         0.181 |      0.808 |        0.295 |
| Reversed Heading            |        0.817 |         0.510 |      0.508 |        0.509 |
| Feigned Braking             |        0.817 |         0.056 |      0.083 |        0.067 |
| Acceleration Multiplication |        0.814 |         0.104 |      0.131 |        0.116 |
| DoS Attack                  |        0.683 |         0.693 |      0.394 |        0.502 |
| Traffic Congestion Sybil    |        0.585 |         0.659 |      0.253 |        0.366 |
| Data Replay                 |        0.750 |         0.324 |      0.245 |        0.279 |

### Highway - high density
| **Attack Type**             | **TP** |  **TN** | **FP** |  **FN** |
|-----------------------------|-------:|--------:|-------:|--------:|
| Time Delay Attack           |  19828 | 2371978 |  94532 |  525032 |
| Constant Position Offset    | 268716 | 2403425 |  83462 |  255767 |
| Random Position Offset      | 587467 | 2315608 |  92950 |   15345 |
| Position Mirroring          |  31939 | 2328496 |  93543 |  557392 |
| Constant Speed Offset       | 145566 | 2380102 |  93259 |  392443 |
| Random Speed Offset         | 462683 | 2221855 |  92521 |  234311 |
| Zero Speed Report           | 161362 | 2658801 |  95337 |   95870 |
| Sudden Stop                 |  37891 | 2579054 | 120485 |  273940 |
| Sudden Constant Speed       |  41729 | 2795231 | 141247 |   33163 |
| Reversed Heading            | 132737 | 2685532 |  90971 |  102130 |
| Feigned Braking             |   5175 | 2786111 | 109382 |  110702 |
| Acceleration Multiplication |  11197 | 2739439 | 103360 |  157374 |
| DoS Attack                  | 254376 | 2342109 |  92599 | 1587633 |
| Traffic Congestion Sybil    | 445048 | 2890719 | 120651 | 2686358 |
| Data Replay                 | 169933 | 2299624 | 141439 |  400374 |

| **Attack Type**             | **Accuracy** | **Precision** | **Recall** | **F1 Score** |
|-----------------------------|-------------:|--------------:|-----------:|-------------:|
| Time Delay Attack           |        0.794 |         0.173 |      0.036 |        0.060 |
| Constant Position Offset    |        0.887 |         0.763 |      0.512 |        0.613 |
| Random Position Offset      |        0.964 |         0.863 |      0.975 |        0.916 |
| Position Mirroring          |        0.784 |         0.255 |      0.054 |        0.089 |
| Constant Speed Offset       |        0.839 |         0.610 |      0.271 |        0.375 |
| Random Speed Offset         |        0.891 |         0.833 |      0.664 |        0.739 |
| Zero Speed Report           |        0.937 |         0.629 |      0.627 |        0.628 |
| Sudden Stop                 |        0.869 |         0.239 |      0.122 |        0.161 |
| Sudden Constant Speed       |        0.942 |         0.228 |      0.557 |        0.324 |
| Reversed Heading            |        0.936 |         0.593 |      0.565 |        0.579 |
| Feigned Braking             |        0.927 |         0.045 |      0.045 |        0.045 |
| Acceleration Multiplication |        0.913 |         0.098 |      0.066 |        0.079 |
| DoS Attack                  |        0.607 |         0.733 |      0.138 |        0.232 |
| Traffic Congestion Sybil    |        0.543 |         0.787 |      0.142 |        0.241 |
| Data Replay                 |        0.820 |         0.546 |      0.298 |        0.385 |

## Comparison of VeReMi Extension vs VeReMi NextGen
The following values show the direct comparison of VeReMi Extension and VeReMi NextGen.

### Optimized Parameter
| **Parameter** | **VeReMi NextGen** | **VeReMi Extension** |
|---------------|-------------------:|---------------------:|
| MPR           |            337.890 |              418.139 |
| MPDN          |             -2.831 |               -4.498 |
| MPS           |             62.946 |               62.329 |
| MPA           |              3.113 |                5.418 |
| MPD           |              5.301 |                5.005 |
| MHC           |            129.667 |               76.239 |
| MDI           |              3.166 |                4.297 |
| MTD           |              1.922 |                4.724 |
| PHT           |              3.472 |                0.398 |
| MMRU          |              1.492 |                0.706 |
| MMRD          |              3.200 |                1.029 |
| MNRS          |              0.000 |                0.679 |


### MBD Results

#### VeReMi NextGen
| **Attack Type**          | **TP** |  **TN** | **FP** | **FN** |
|--------------------------|-------:|--------:|-------:|-------:|
| Constant Position Offset | 330929 | 3801324 |  16306 | 505372 |
| Random Speed Offset      | 673830 | 3538197 |  15213 | 426691 |
| Sudden Stop              |   4330 | 4285363 |  21681 | 342557 |

| **Attack Type**          | **Accuracy** | **Precision** | **Recall** | **F1 Score** |
|--------------------------|-------------:|--------------:|-----------:|-------------:|
| Constant Position Offset |        0.888 |         0.953 |      0.396 |        0.559 |
| Random Speed Offset      |        0.905 |         0.978 |      0.612 |        0.753 |
| Sudden Stop              |        0.922 |         0.166 |      0.012 |        0.023 |

#### VeReMi Extension
| **Attack Type**          | **TP** |  **TN** | **FP** | **FN** |
|--------------------------|-------:|--------:|-------:|-------:|
| Constant Position Offset | 276226 | 8310190 |   3325 |  59103 |
| Random Speed Offset      | 290236 |  821323 |  15416 |  42698 |
| Sudden Stop              | 141817 |  899750 |   3150 | 124956 |

| **Attack Type**          | **Accuracy** | **Precision** | **Recall** | **F1 Score** |
|--------------------------|-------------:|--------------:|-----------:|-------------:|
| Constant Position Offset |        0.947 |         0.988 |      0.824 |        0.898 |
| Random Speed Offset      |        0.950 |         0.950 |      0.872 |        0.909 |
| Sudden Stop              |        0.890 |         0.978 |      0.532 |        0.689 |
