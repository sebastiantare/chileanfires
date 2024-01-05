#wildfiresapi/router.py
from wildfiresapi.viewsets import WildfiresViewset, WildfiresViewset12Months
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'wildfires', WildfiresViewset)
router.register(r'wildfires12months', WildfiresViewset12Months, basename='wildfires12months')
