from django.contrib import admin

from air_service.models import (
    Country,
    City,
    Airport,
    AirplaneType,
    Airplane,

)


# class TicketInLine(admin.TabularInline):
#     model = Ticket
#     extra = 1
#

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     inlines = (TicketInLine,)


admin.site.register(Country)
admin.site.register(City)
admin.site.register(Airport)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
