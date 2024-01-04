#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Budy
# Copyright (c) 2008-2024 Hive Solutions Lda.
#
# This file is part of Hive Budy.
#
# Hive Budy is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Budy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Budy. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__copyright__ = "Copyright (c) 2008-2024 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import zipfile
import tempfile
import mimetypes

import appier

from . import base
from . import product

BASE_URL = "http://localhost:8080/"


class Media(base.BudyBase):
    label = appier.field(index=True)

    order = appier.field(type=int, index=True)

    size = appier.field(index=True)

    unique = appier.field(index=True, safe=True)

    file = appier.field(type=appier.File, private=True)

    @classmethod
    def validate(cls):
        return super(Media, cls).validate() + [
            appier.not_null("description"),
            appier.not_empty("description"),
            appier.not_null("label"),
            appier.not_empty("label"),
            appier.not_null("order"),
            appier.not_null("file"),
            appier.not_empty("file"),
        ]

    @classmethod
    def list_names(cls):
        return ["id", "description", "label", "order", "size"]

    @classmethod
    def order_name(cls):
        return ["id", -1]

    @classmethod
    def is_visible(cls):
        return False

    @classmethod
    @appier.operation(
        name="Import Media",
        parameters=(
            ("Media File", "file", "file"),
            ("Empty source", "empty", bool, False),
        ),
    )
    def import_media_s(cls, file, empty, strict=False):
        _file_name, mime_type, data = file
        is_zip = mime_type in ("application/zip", "application/octet-stream")
        if not is_zip and strict:
            raise appier.OperationalError(message="Invalid MIME type '%s'" % mime_type)
        buffer = appier.legacy.BytesIO(data)
        file = zipfile.ZipFile(buffer, mode="r")
        target = tempfile.mkdtemp()
        try:
            file.extractall(target)
        finally:
            file.close()

        if empty:
            cls.delete_c()

        names = os.listdir(target)
        for name in names:
            path = os.path.join(target, name)
            is_dir = os.path.isdir(path)
            if is_dir:
                image_names = os.listdir(path)
            else:
                path = target
                image_names = [name]
            for image_name in image_names:
                base, extension = os.path.splitext(image_name)
                if not extension in (".png", ".jpeg", ".jpg"):
                    continue

                content_type, _encoding = mimetypes.guess_type(image_name, strict=False)

                product_id = base
                label = "undefined"
                order = 0
                size = "large"

                base_s = base.split("_")
                if len(base_s) >= 1:
                    product_id = base_s[0]
                if len(base_s) >= 2:
                    order = int(base_s[1])
                if len(base_s) >= 3:
                    label = base_s[2]
                if len(base_s) >= 4:
                    size = base_s[3]

                description = "%s_%s_%s" % (product_id, label, size)

                image_path = os.path.join(path, image_name)
                image_file = open(image_path, "rb")
                try:
                    image_data = image_file.read()
                finally:
                    image_file.close()

                media = Media(
                    description=description,
                    label=label,
                    order=order,
                    size=size,
                    file=appier.File((product_id, content_type, image_data)),
                )
                media.save()

                _product = product.Product.get(product_id=product_id, raise_e=False)
                if not _product:
                    continue

                _product.images.append(media)
                _product.save()

    @classmethod
    def _build(cls, model, map):
        super(Media, cls)._build(model, map)
        id = model.get("id", None)
        if id:
            model["url"] = cls._get_url(id)
            for format in ("png", "jpeg", "webp"):
                model["url_" + format] = cls._get_url(id, format=format)

    @classmethod
    def _plural(cls):
        return "Media"

    @classmethod
    def _get_url(cls, id, format=None, absolute=True):
        app = appier.get_app()
        if format:
            return app.url_for(
                "media_api.data_format",
                id=id,
                format=format,
                prefix="/",
                absolute=absolute,
            )
        else:
            return app.url_for("media_api.data", id=id, prefix="/", absolute=absolute)

    def get_url(self, format=None):
        return self.__class__._get_url(self.id, format=format)

    def convert_image(self, format, background=None, **kwargs):
        import PIL.Image

        kwargs = dict(kwargs)
        buffer = appier.legacy.BytesIO()
        image = PIL.Image.open(appier.legacy.BytesIO(self.file.data))
        if format in ("jpeg",) and not background:
            background = "ffffff"
        if background:
            image_background = PIL.Image.new(
                "RGB", (image.width, image.height), color="#" + background
            )
            if image.mode == "RGBA":
                image_background.paste(image, mask=image)
            else:
                image_background.paste(image)
            image = image_background
        image.save(buffer, format=format, **kwargs)
        return buffer

    @appier.operation(
        name="Generate Thumbnail",
        parameters=(
            ("Width", "width", int),
            ("Height", "height", int),
            ("Format", "format", str, "png"),
            ("Suffix", "suffix", str, "thumbnail"),
        ),
        factory=True,
    )
    def thumbnail_s(self, width=None, height=None, format="png", suffix="thumbnail"):
        cls = self.__class__
        media = self.reload(rules=False)
        builder = appier.image(
            width=width or height, height=height or width, format=format
        )
        image = builder(media.file)
        data = image.resize()
        name = "%s.%s" % (suffix, format)
        mime, _encoding = mimetypes.guess_type(name, strict=False)
        thumbnail = cls(
            description=media.description,
            label=suffix,
            order=media.order,
            size=suffix,
            unique="%s-%s" % (media.unique, suffix),
            file=appier.File((name, mime, data)),
        )
        thumbnail.save()
        return thumbnail

    @appier.link(name="View")
    def view_url(self, absolute=False):
        return self.owner.url_for(
            "media_api.data", id=self.id, prefix="/", absolute=absolute
        )
