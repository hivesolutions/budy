#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Budy
# Copyright (c) 2008-2016 Hive Solutions Lda.
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

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import appier

from . import base

class Group(base.BudyBase):

    name = appier.field(
        index = True,
        default = True
    )

    order = appier.field(
        type = int,
        index = True
    )

    image_url = appier.field(
        index = True,
        meta = "url"
    )

    images = appier.field(
        type = appier.references(
            "Media",
            name = "id"
        )
    )

    @classmethod
    def validate(cls):
        return super(Group, cls).validate() + [
            appier.not_null("name"),
            appier.not_empty("name")
        ]

    @classmethod
    def list_names(cls):
        return ["id", "name"]

    @classmethod
    def ensure_s(cls, name):
        group = cls.get(name = name, raise_e = False)
        if group: return group
        group = cls(name = name)
        group.save()
        return group

    def pre_validate(self):
        base.BudyBase.pre_validate(self)
        self.build_images()

    def build_images(self):
        thumbnail = self.get_image(size = "thumbnail", order = 1)
        thumbnail = thumbnail or self.get_image(size = "thumbnail")
        image = self.get_image(size = "large", order = 1)
        image = image or self.get_image(size = "large")
        self.thumbnail_url = thumbnail.get_url() if thumbnail else None
        self.image_url = image.get_url() if image else None

    def get_image(self, size = None, order = None):
        for image in self.images:
            is_size = size == None or image.size == size
            if not is_size: continue
            is_order = order == None or image.order == order
            if not is_order: continue
            return image
        return None

    @appier.operation(
        name = "Add Image",
        parameters = (
            (
                "Image",
                "image",
                appier.reference("Media", name = "id")
            ),
        )
    )
    def add_image_s(self, image):
        if not image: return
        if image in self.images: return
        self.images.append(image)
        self.save()

    @appier.operation(
        name = "Remove Image",
        parameters = (
            (
                "Image",
                "image",
                appier.reference("Media", name = "id")
            ),
        )
    )
    def remove_image_s(self, image):
        if not image: return
        if not image in self.images: return
        self.images.remove(image)
        self.save()

    @appier.operation(
        name = "Upload Image",
        parameters = (
            ("File", "file", "file"),
            ("Label", "label", str, "main"),
            ("Size", "size", str, "large")
        )
    )
    def upload_image_s(self, file, label, size):
        from . import media
        if not file: return
        media = media.Media(
            description = self.name,
            label = label,
            order = 1,
            size = size,
            file = appier.File(file)
        )
        media.save()
        self.images.append(media)
        self.save()
