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

import mimetypes

import appier

import budy

from . import root


class MediaAPIController(root.RootAPIController):
    @appier.route("/api/media", "GET", json=True)
    def list(self):
        object = appier.get_object(alias=True, find=True)
        media = budy.Media.find(map=True, **object)
        return media

    @appier.route("/api/media/<int:id>/data", "GET", json=True)
    def data(self, id):
        media = budy.Media.get(id=id, fields=("file",), rules=False)
        file = media.file
        if not file:
            raise appier.NotFoundError(message="File not found for media '%d'" % id)
        return self.send_file(
            file.data,
            name="%d" % id,
            content_type=file.mime,
            etag=file.etag,
            cache=True,
        )

    @appier.route("/api/media/<int:id>/data.<str:format>", "GET", json=True)
    def data_format(self, id, format):
        background = self.field("background", None)
        quality = self.field("quality", 90, cast=int)
        media = budy.Media.get(id=id, fields=("file",), rules=False)
        file = media.file
        if not file:
            raise appier.NotFoundError(message="File not found for media '%d'" % id)
        extension = mimetypes.guess_extension(file.mime or "")
        mime, _encoding = mimetypes.guess_type("data." + format)
        if extension and extension[1:] == format:
            return self.send_file(
                file.data,
                name="%d.%s" % (id, format),
                content_type=file.mime,
                etag=file.etag,
                cache=True,
            )
        buffer = media.convert_image(
            format, background=background, **dict(quality=quality)
        )
        return self.send_file(
            buffer.getvalue(),
            name="%d.%s" % (id, format),
            content_type=mime,
            etag=file.etag,
            cache=True,
        )
