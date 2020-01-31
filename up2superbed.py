# -*- coding: utf-8 -*-
"""
    up2superbed
    ~~~~~~~~~~~~

    Save uploaded pictures in superbed.cn

    :copyright: (c) 2020 by staugur.
    :license: BSD 3-Clause, see LICENSE for more details.
"""

__version__ = '0.1.0'
__author__ = 'staugur <staugur@saintic.com>'
__hookname__ = 'up2superbed'
__description__ = '将图片保存到聚合图床'

import requests
from flask import g

intpl_hooksetting = u'''
<fieldset class="layui-elem-field">
    <legend>聚合图床（{% if "up2superbed" in g.site.upload_includes %}使用中{% else %}未使用{% endif %}）</legend>
    <div class="layui-field-box">
        <div class="layui-form-item">
            <label class="layui-form-label"> 聚合图床密钥</label>
            <div class="layui-input-block">
                <input type="text" name="superbed_token" value="{{ g.site.superbed_token }}" placeholder="Api Token @ superbed.cn"
                    autocomplete="off" class="layui-input">
            </div>
        </div>
    </div>
</fieldset>
'''


def upimg_save(**kwargs):
    res = dict(code=1)
    try:
        filename = kwargs["filename"]
        stream = kwargs["stream"]
        if not filename or not stream:
            return ValueError
    except (KeyError, ValueError):
        res.update(msg="Parameter error")
    else:
        token = g.cfg.superbed_token
        if not token:
            res.update(msg="The superbed.cn parameter error")
        else:
            files = {
                'file': (
                    filename, stream, 'image/%s' % filename.split(".")[-1]
                )
            }
            headers = {
                "User-Agent": "picbed-up2superbed/%s" % __version__,
            }
            try:
                r = requests.post(
                    "https://api.superbed.cn/upload",
                    files=files,
                    data=dict(token=token, v=2),
                    headers=headers,
                    timeout=30
                )
            except requests.exceptions.RequestException as e:
                res.update(msg=e.message)
            else:
                result = r.json()
                if result.pop("err", 1) == 0:
                    res.update(code=0, src=result.pop("url"))
                    res.update(result)
    return res


def upimg_delete(**kwargs):
    result = kwargs.get("save_result")
    imgId = result.get("id")
    if imgId:
        requests.post(
            "https://pic.superbed.cn/info/%s" % imgId,
            data=dict(token=g.cfg.superbed_token, action="delete")
        ).json()
