import typing
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    scope: typing.Mapping[str, typing.Any]

    receive: typing.Callable[[], typing.Awaitable[object]]
    send: typing.Callable[[object], typing.Awaitable[None]]


class RestaurantManager:
    def __init__(self):
        """Instantiate the restaurant manager.

        This is called at the start of each day before any staff get on
        duty or any orders come in. You should do any setup necessary
        to get the system working before the day starts here; we have
        already defined a staff dictionary.
        """
        self.staff = {}

    async def __call__(self, request: Request):
        """Handle a request received.

        This is called for each request received by your application.
        In here is where most of the code for your system should go.

        :param request: request object
            Request object containing information about the sent
            request to your application.
        """
        
        request_type = request.scope.get("type")
        if not request_type:
            raise Exception("type not specified in scope")

        if request_type == "order":
            await self.distribute_order(request)
        else:
            self.manage_staff_availablity(request)
    
    async def distribute_order(self , request):
        """Handle a requested order.

        :param request: request object
            Request object containing information about the order.
        """
        incoming_order = await request.receive()
        
        # pick a available(on duty) staff by matching order's speciality
        picked_staff = self.pick_available_staff_by_matching_speciality(request.scope["speciality"])
        
        # send order to staff
        await picked_staff.send(incoming_order)
        
        # staff receive requested order
        staff_result = await picked_staff.receive()
        
        # staff result send back for order acknowledgement
        await request.send(staff_result)
    
    def pick_available_staff_by_matching_speciality(self, speciality: list[str]):
        """Pick a available staff randomly matching with provided speciality.

        :param request: speciality list[str]
            list of required specialities.
        :return: Request
            single staff
        """
        matching_staffs = []
        for _, staff in self.staff.items():
            if speciality in staff.scope['speciality']:
                matching_staffs.append(staff)
        return random.choice(matching_staffs) if matching_staffs else None

    def manage_staff_availablity(self, request: Request):
        """Handle a requested staff availablity[onduty or offduty]

        :param request: request object
            Request object containing information about staff.
        """
        staff_id = request.scope["id"]
        if request.scope["type"] == "staff.offduty":
            del self.staff[staff_id]
        else:
            self.staff[staff_id] = request
