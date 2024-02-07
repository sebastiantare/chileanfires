# wildfiresapi/router.py
from wildfiresapi.viewsets import \
        WildfiresViewset, \
        WildfiresByDateViewset, \
        WildfiresViewset12Months
from rest_framework import routers


router = routers.DefaultRouter()

router.register(r'wildfires',
                WildfiresViewset,
                basename='wildfires')
router.register(r'wildfires12months',
                WildfiresViewset12Months,
                basename='wildfires12months')
router.register(r'wildfiresbydate',
                WildfiresByDateViewset,
                basename='wildfiresbydate')
