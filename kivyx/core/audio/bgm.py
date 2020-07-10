__all__ = ('Bgm', )

from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, AliasProperty
from kivy.core.audio import Sound
import asynckivy as ak

from kivyx.properties import AutoCloseProperty


class Bgm(EventDispatcher):
    '''kivy.core.audio.Sound with some features below:
    
    - fade-in/out
    - Remembers the last position, and resumes from there. (Only if
    the audio provider supports seeking.)
    '''

    max_volume = NumericProperty(1.)

    fade_in_duration = NumericProperty(1.)
    '''Duration of fade-in transition. '''

    fade_out_duration = NumericProperty(1.)
    '''Duration of fade-out transition. '''

    def _get_pos(self):
        return self.sound.get_pos() if self._is_playing else self._pos
    def _set_pos(self, new_pos):
        length = self._length
        if length is None:
            # 'length' is not available right now, so normalize the pos later
            self._pos = new_pos
            return
        sound = self.sound
        # normalize
        new_pos = (new_pos % length) if sound.loop else min(length, new_pos)
        self._pos = new_pos
        if self._is_playing:
            sound.seek(new_pos)
    pos = property(_get_pos, _set_pos)
    '''The current position of the sound.'''

    def __init__(self, sound:Sound, **kwargs):
        self._length = None
        self._pos = 0.
        self._needs_to_play = ak.Event()
        self._needs_to_stop = ak.Event()
        self.sound = sound

        self._is_playing = False
        '''we need an own flag because 'Sound.state' is not *real* '''

        internal_delay = kwargs.pop('internal_delay', .5)
        '''The *real* state of the Sound doesn't seem to change as soon as
        'Sound.play()' is called, so we need to wait for a while until it
        actually does. This might depend on the audio provider. At least
        audio_gstreamer needs this.
        '''

        super().__init__(**kwargs)
        ak.start(self._main(internal_delay=internal_delay))
        
    async def _main(self, *, internal_delay):
        sound = self.sound
        needs_to_play = self._needs_to_play
        needs_to_stop = self._needs_to_stop
        sleep = await ak.create_sleep(internal_delay)
        try:
            self._length = length = \
                await _get_sound_length(sound, internal_delay)
            if self._pos != 0.:
                self.pos = self._pos  # normalize
            while True:
                sound.volume = 0.
                await needs_to_play.wait()
                needs_to_play.clear()
                sound.play()
                await sleep()
                sound.seek(self._pos)
                self._is_playing = True
                await ak.animate(
                    sound, volume=self.max_volume, d=self.fade_in_duration, )
                await needs_to_stop.wait()
                needs_to_stop.clear()
                await ak.animate(sound, volume=0., d=self.fade_out_duration, )
                self._pos = sound.get_pos()
                self._is_playing = False
                sound.stop()
                await sleep()
        finally:
            sound.stop()

    def play(self, *args, **kwargs):
        self._needs_to_stop.clear()
        self._needs_to_play.set()

    def stop(self, *args, **kwargs):
        self._needs_to_play.clear()
        self._needs_to_stop.set()


async def _get_sound_length(sound, internal_delay):
    sound.volume = 0.
    sound.play()
    await ak.sleep(internal_delay)
    length = sound.length
    sound.stop()
    await ak.sleep(internal_delay)
    return length
