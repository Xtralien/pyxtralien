#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Mixin(object):
    pass


class SMUProviderMixin(Mixin):
    def __init__(self, *args, **kwargs):
        super(SMUProviderMixin, self).__init__(*args, **kwargs)
        print("SMU provider started")


class VSenseProviderMixin(Mixin):
    def __init__(self, *args, **kwargs):
        super(VSenseProviderMixin, self).__init__(*args, **kwargs)
        print("VSense provider started")


class X100(SMUProviderMixin, VSenseProviderMixin):
    def __init__(self, *args, **kwargs):
        super(X100, self).__init__(*args, **kwargs)
        print("X100 started")
