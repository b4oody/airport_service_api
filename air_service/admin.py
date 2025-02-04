from django.contrib import admin

from air_service.models import (
    Country,
    City,
    Airport,
    AirplaneType,
    Airplane,
    Route,
    Crew,
    Flight,
    Order,
    Ticket

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
admin.site.register(Route)
admin.site.register(Crew)
admin.site.register(Flight)
admin.site.register(Ticket)
admin.site.register(Order)
