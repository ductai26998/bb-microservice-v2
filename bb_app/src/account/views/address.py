from urllib.parse import unquote

import requests


class Address:
    @classmethod
    def __init__(self, *args, **kwargs):
        self.address = kwargs.get("address")
        self.province = kwargs.get("province")
        self.district = kwargs.get("district")
        self.ward = kwargs.get("ward")
        self.hamlet = kwargs.get("hamlet")
        self.lat = kwargs.get("lat")
        self.lng = kwargs.get("lng")
        self.position_url = kwargs.get("position_url")

    @classmethod
    def set_address_from_url(self, url: str):
        if not url:
            return
        self.position_url = url
        url = self.get_origin_url_from_short_url(url)
        url = unquote(url)
        url = url.replace("https://www.google.com/maps/place/", "")
        types = url.split("/")
        self.address = types[0].replace("+", " ")
        sub_addresses = self.address.split(", ")
        length_address = len(sub_addresses)
        if length_address >= 2:
            self.province = sub_addresses[-2]
            if length_address >= 3:
                self.district = sub_addresses[-3]
                if length_address >= 4:
                    self.ward = sub_addresses[-4]
                    if length_address >= 5:
                        self.hamlet = sub_addresses[-5]

        location = types[1].replace("@", "").split(",")
        self.lat = location[0]
        self.lng = location[1]

    @classmethod
    def get_position_from_url(self, url: str):
        if not url:
            return
        url = self.get_origin_url_from_short_url(url)
        url = unquote(url)
        url = url.replace("https://www.google.com/maps/place/", "")
        types = url.split("/")
        location = types[1].replace("@", "").split(",")
        lat = location[0]
        lng = location[1]
        return (lat, lng)

    @classmethod
    def get_origin_url_from_short_url(self, url: str):
        session = requests.Session()  # so connections are recycled
        resp = session.head(url, allow_redirects=True)
        return resp.url


# class AddressViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = models.Address.objects.all()
#     serializer_class = AddressSerializer
