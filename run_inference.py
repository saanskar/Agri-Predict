import asyncio
from backend.app.services.inference.runtime import ArtifactEnsembleInferenceService
from backend.app.schemas import SoilSample
from backend.app.services.weather.types import WeatherSnapshot

async def main():
    # Set the path to your artifacts directory
    artifacts_dir = r"E:\Capstone - Copy\Agri\artifacts"
    service = ArtifactEnsembleInferenceService(artifacts_dir=artifacts_dir)

    # Example input (replace with your real data)
    soil = SoilSample(n=90, p=42, k=43, ph=6.5)
    weather = WeatherSnapshot(temperature_c=27.0, relative_humidity_pct=80.0, rainfall_mm=200.0)

    # Get top 3 crop recommendations
    recommendations = await service.recommend(soil=soil, weather=weather, top_k=3)
    for rec in recommendations:
        print(f"Crop: {rec.crop}, Probability: {rec.probability:.3f}")

if __name__ == "__main__":
    asyncio.run(main())
