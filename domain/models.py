from dataclasses import dataclass, field


@dataclass
class StacAsset:
    key: str
    href: str
    media_type: str
    title: str
    roles: list

    @property
    def is_cog(self):
        return (
            "cloud-optimized" in self.media_type.lower()
            or self.media_type == "image/tiff"
            or "geotiff" in self.media_type.lower()
        )

    @property
    def is_downloadable(self):
        return bool(self.href)

    @classmethod
    def from_dict(cls, key, data):
        return cls(
            key=key,
            href=data.get("href", ""),
            media_type=data.get("type", ""),
            title=data.get("title", key),
            roles=data.get("roles", []),
        )


@dataclass
class StacItem:
    id: str
    collection: str
    datetime: str
    geometry: dict
    bbox: list
    properties: dict
    assets: dict
    links: list
    raw_data: dict = field(default_factory=dict, repr=False)

    @property
    def cloud_cover(self):
        return self.properties.get("eo:cloud_cover")

    @property
    def thumbnail_url(self):
        for asset in self.assets.values():
            if "thumbnail" in asset.roles:
                return asset.href
        return None

    @property
    def cog_assets(self):
        return {k: v for k, v in self.assets.items() if v.is_cog}

    def preferred_asset(self, user_choice=None):
        if user_choice and user_choice in self.assets:
            asset = self.assets[user_choice]
            if asset.is_cog:
                return asset

        if "tci" in self.assets and self.assets["tci"].is_cog:
            return self.assets["tci"]

        cogs = self.cog_assets
        if cogs:
            return next(iter(cogs.values()))

        return None

    def first_downloadable_asset(self):
        cog = self.preferred_asset()
        if cog:
            return cog
        for asset in self.assets.values():
            if asset.is_downloadable:
                return asset
        return None

    @classmethod
    def from_dict(cls, data):
        assets_raw = data.get("assets", {})
        assets = {k: StacAsset.from_dict(k, v) for k, v in assets_raw.items()}

        dt = data.get("properties", {}).get("datetime", "")

        return cls(
            id=data.get("id", ""),
            collection=data.get("collection", ""),
            datetime=dt,
            geometry=data.get("geometry", {}),
            bbox=data.get("bbox", []),
            properties=data.get("properties", {}),
            assets=assets,
            links=data.get("links", []),
            raw_data=data,
        )


@dataclass
class StacCollection:
    id: str
    title: str
    description: str
    spatial_extent: list
    temporal_extent: list
    raw_data: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data):
        extent = data.get("extent", {})
        spatial = extent.get("spatial", {}).get("bbox", [[]])[0]
        temporal = extent.get("temporal", {}).get("interval", [[]])[0]

        return cls(
            id=data.get("id", ""),
            title=data.get("title", data.get("id", "")),
            description=data.get("description", ""),
            spatial_extent=spatial,
            temporal_extent=temporal,
            raw_data=data,
        )


@dataclass
class SearchParams:
    bbox: list = None
    intersects: dict = None
    datetime_start: str = None
    datetime_end: str = None
    collections: list = None
    limit: int = 10
    page: int = 1

    def to_query_params(self):
        params = {}

        if self.bbox:
            params["bbox"] = ",".join(str(v) for v in self.bbox)

        if self.datetime_start and self.datetime_end:
            params["datetime"] = f"{self.datetime_start}/{self.datetime_end}"
        elif self.datetime_start:
            params["datetime"] = self.datetime_start
        elif self.datetime_end:
            params["datetime"] = f"../{self.datetime_end}"

        if self.collections:
            params["collections"] = ",".join(self.collections)

        params["limit"] = str(self.limit)
        params["page"] = str(self.page)

        return params

    def to_post_body(self):
        body = {}

        if self.bbox:
            body["bbox"] = self.bbox

        if self.intersects:
            body["intersects"] = self.intersects

        if self.datetime_start and self.datetime_end:
            body["datetime"] = f"{self.datetime_start}/{self.datetime_end}"
        elif self.datetime_start:
            body["datetime"] = self.datetime_start
        elif self.datetime_end:
            body["datetime"] = f"../{self.datetime_end}"

        if self.collections:
            body["collections"] = self.collections

        body["limit"] = self.limit
        body["page"] = self.page

        return body


@dataclass
class SearchResult:
    items: list
    matched: int
    returned: int
    next_page: int = None
    prev_page: int = None
