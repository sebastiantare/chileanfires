# 🔥🔥🔥 Chilean Fires Analysis 🔥🔥🔥

In this project I analyze data from [NASA's FIRMS](https://earthdata.nasa.gov/firms) to understand which places have the most likelihood to catch on fire.

**Done:**
- Generate clusters of fires grouped by time.
  
[great-fire2017.webm](https://github.com/sebastiantare/chileanfires/assets/106767449/1c7a7a55-a0a7-4444-92a1-b9a818edb293)

- Generate MBR out of clusters.

![image](https://github.com/sebastiantare/chileanfires/assets/106767449/dfb10585-ca64-4d1b-a3d6-3e038498dc86)

- Measure intersection of MBR of fire clusters in time.

![image](https://github.com/sebastiantare/chileanfires/assets/106767449/20d75a46-d768-445e-b35a-35026c41754e)

    The mean time is 303.95 days between fire MBR overlapping.
    The median time is 2.0 days between fire MBR overlapping.
    The standard deviation is 572.5 days between fire MBR overlapping.
    The most common time is 1 days (most repeated).
    The 50 percentile is 2.0 days.
    The 75 percentile is 412.5 days.
    The 80 percentile is 744.0 days.
    The 85 percentile is 829.8 days.


**TODO:**

- Setup dashboard to visualize active fires.
- Get areas with the most likelihood of fire.
- Understand how climate variables (from Meteochile) affect the number of fires.
- Build a forecasting model for the number of fires based on climate variables.
