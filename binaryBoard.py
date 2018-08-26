#!/usr/bin/python3

import gpiozero


class binaryBoard(CompositeDevice):    
    """
    Extends :class:`CompositeDevice` and represents a generic button board or
    collection of buttons.
    :param int \*pins:
        Specify the GPIO pins that the buttons of the board are attached to.
        You can designate as many pins as necessary.
    :param bool pull_up:
        If ``True`` (the default), the GPIO pins will be pulled high by
        default. In this case, connect the other side of the buttons to
        ground. If ``False``, the GPIO pins will be pulled low by default. In
        this case, connect the other side of the buttons to 3V3. This
        parameter can only be specified as a keyword parameter.
    :param float bounce_time:
        If ``None`` (the default), no software bounce compensation will be
        performed. Otherwise, this is the length of time (in seconds) that the
        buttons will ignore changes in state after an initial change. This
        parameter can only be specified as a keyword parameter.
    :param float hold_time:
        The length of time (in seconds) to wait after any button is pushed,
        until executing the :attr:`when_held` handler. Defaults to ``1``. This
        parameter can only be specified as a keyword parameter.
    :param bool hold_repeat:
        If ``True``, the :attr:`when_held` handler will be repeatedly executed
        as long as any buttons remain held, every *hold_time* seconds. If
        ``False`` (the default) the :attr:`when_held` handler will be only be
        executed once per hold. This parameter can only be specified as a
        keyword parameter.
    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    :param \*\*named_pins:
        Specify GPIO pins that buttons of the board are attached to,
        associating each button with a property name. You can designate as
        many pins as necessary and use any names, provided they're not already
        in use by something else.
    """

    ### devices.py
    # Device
    # CompositeDevice
    ### board.py
    
    def __init__(self, *args, **kwargs):
        pull_up = kwargs.pop('pull_up', True)
        bounce_time = kwargs.pop('bounce_time', None)
        hold_time = kwargs.pop('hold_time', 1)
        hold_repeat = kwargs.pop('hold_repeat', False)
        pin_factory = kwargs.pop('pin_factory', None)
        order = kwargs.pop('_order', None)
        super(ButtonBoard, self).__init__(
            *(
                Button(pin, pull_up, bounce_time, hold_time, hold_repeat)
                for pin in args
                ),
            _order=order,
            pin_factory=pin_factory,
            **{
                name: Button(pin, pull_up, bounce_time, hold_time, hold_repeat)
                for name, pin in kwargs.items()
                })
        def get_new_handler(device):
            def fire_both_events():
                device._fire_events()
                self._fire_events()
            return fire_both_events
        for button in self:
            button.pin.when_changed = get_new_handler(button)
        self._when_changed = None
        self._last_value = None
        # Call _fire_events once to set initial state of events
        self._fire_events()
        self.hold_time = hold_time
        self.hold_repeat = hold_repeat

    @property
    def pull_up(self):
        """
        If True, the device uses a pull-up resistor to set the GPIO pin
        "high" by default.
        """
        return self[0].pull_up

    @property
    def when_changed(self):
        return self._when_changed

    @when_changed.setter
    def when_changed(self, value):
        self._when_changed = self._wrap_callback(value)

        
    def _fire_changed(self):
        if self.when_changed:
            self.when_changed()

    def _fire_events(self):
        super(ButtonBoard, self)._fire_events()
        old_value = self._last_value
        new_value = self._last_value = self.value
        if old_value is None:
            # Initial "indeterminate" value; don't do anything
            pass
        elif old_value != new_value:
            self._fire_changed()

