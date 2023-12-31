# 🔥🔥🔥 Chilean Fires Analysis 🔥🔥🔥

<div align="center">
<pre>
  <b>Objective</b>
  <p>Visualize wildfires and estimate areas with the highest likelihood of fires in Chile.</p>
</pre>

</div>

In this project I analyze data from [NASA's FIRMS](https://earthdata.nasa.gov/firms) to understand which places have the most likelihood to catch on fire.

## Project Progression ![](https://geps.dev/progress/50)

## What's already Done
- Generate clusters of fires grouped by time.
  
[great-fire2017.webm](https://github.com/sebastiantare/chileanfires/assets/106767449/1c7a7a55-a0a7-4444-92a1-b9a818edb293)

- Generate MBR out of clusters.

![image](https://github.com/sebastiantare/chileanfires/assets/106767449/dfb10585-ca64-4d1b-a3d6-3e038498dc86)

- Measure intersection of MBR of fire clusters in time.

![image](https://github.com/sebastiantare/chileanfires/assets/106767449/20d75a46-d768-445e-b35a-35026c41754e)

- Backend to serve the Chilean Fires Dashboard -> [incendioschile.online](https://incendioschile.online)

![image](https://github.com/sebastiantare/chileanfires/assets/106767449/72c3f9bd-f868-480e-aeb2-813dee8452d3)

- More data sources added from 2 more satellites.
- Updated UI with the new version with Tailwind.

  ![image](https://github.com/sebastiantare/chileanfires/assets/106767449/fc214feb-1459-45f0-ae42-b5e476fa454e)


## TODO

- Understand how climate variables (from Meteochile) affect the number of fires.
- Build a forecasting model for the number of fires based on climate variables.
- Get areas with the most likelihood of fire.
- Plot areas with the highest likelihood of fires in the Dashboard.

## TechStack

- Python 3.10
- Django
- PostgreSQL
- Conda
- React

## Contributing

1. Fork it (<https://github.com/sebastiantare/chileanfires/fork>)
2. Create your feature branch (`git checkout -b feature/newFeature`)
3. Commit your changes (`git commit -am 'Fixed new feature'`)
4. Push to the branch (`git push origin feature/newFeature`)
5. Create a new Pull Request
