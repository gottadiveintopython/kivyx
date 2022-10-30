'''
*(Tested on CPython3.9.7 + Kivy2.1.0)*

BGM再生を手助けするmodule

これが要った理由
----------------

このような物が要った理由は :class:`kivy.core.audio.Sound` がそのままでは扱い難かったからです。
例えば :meth:`kivy.core.audio.Sound.seek` の説明には

  Most sound providers cannot seek when the audio is stopped. Play then seek.

とありますが単純に

.. code-block::

   sound = SoundLoader.load(...)
   sound.play()
   sound.seek(...)

として良いかというとそうではなく、実際には ``.play()`` の後に少し間を置かないと期待通りに動きませんでした。

.. code-block::

   sound = SoundLoader.load(...)
   sound.play()
   await async_library.sleep(...)
   sound.seek(...)

そしてどうやらこれは ``.seek()`` に限った話ではなく、
``.play()`` や ``.stop()`` を呼んだ後は少し間を置いてから ``sound`` に触らないと安定しないようです。
つまり :class:`kivy.core.audio.Sound` を直接触るコードは仕様にすら書かれていないのに必要な *間* でコードが汚されてしまう事になります。

そこでこのmoduleの出番です。
このmoduleは *間* を完全に覆い隠すのに加えBGM再生に必要になると思われる次の機能を提供します。

* 音を鳴らす時には前回停めた位置から再開。
* 音を停める時には徐々に音量を下げる。
* 音を鳴らす時には徐々に音量を上げる。

使い方
------

もしアプリが一種類のBGMしか鳴らさないのであれば :class:`Bgm` だけで十分です。

.. code-block::

   from kivy.core.audio import SoundLoader
   from kivyx.misc.bgmplayer import Bgm

   sound = SoundLoader.load(r"path/to/bgm.ogg")
   sound.loop = True
   bgm = Bgm(sound)
   
   # 鳴らしたくなったら
   bgm.play()

   # 停めたくなったら
   bgm.stop()

そして複数のBGMがある場合は :class:`BgmPlayer` が使えます。

.. code-block::

   from kivyx.misc.bgmplayer import BgmPlayer

   bgmplayer = BgmPlayer()
   bgmplayer.play(r"path/to/bgm1.ogg")  # bgm1.oggが鳴る
   bgmplayer.play(r"path/to/bgm2.ogg")  # bgm1.oggが停まりbgm2.oggが鳴る
   bgmplayer.play(r"path/to/bgm1.ogg")  # bgm2.oggが停まりbgm1.oggが前回停まった位置から鳴る
   bgmplayer.stop()                     # bgm1.oggが停まる

:class:`BgmPlayer` は既定では一度読み込んだBGMはずっと持ち続けるので次回以降の再生が早くなります。
言うまでもなくこれはメモリを惜しみなく使っている事によります。
もしこの振る舞いを良しとせずメモリの使用量を抑えたいのであれば :class:`MemoryEfficientLoader` が使えます。

.. code-block::

   from kivyx.misc.bgmplayer import BgmPlayer, MemoryEfficientLoader

   bgmplayer = BgmPlayer(loader=MemoryEfficientLoader())

:class:`MemoryEfficientLoader` はBGMが別の物に切り替えられ次第すぐに以前の物を棄てるのでメモリの使用量が抑えられる...はずです [#hazudearu]_ 。
反面切り替えられる度に :class:`kivy.core.audio.Sound` を作り直すので二回目以降であってもあまり再生は早くならないです [#os_cache]_ 。

Loaderの自作
~~~~~~~~~~~~

Loaderは自作することもできます。例えば以下のように予めBGMを一括で読み込んでおけば再生開始時の遅延を限りなく抑えられるでしょう。

.. code-block::

   loader = {
       fn: (sound := SoundLoader.load(fn), setattr(sound, 'loop', True), ) and Bgm(sound)
       for fn in filenames
   }
   bgmplayer = BgmPlayer(loader=loader)

loaderは ``loader[key]`` という式で :class:`Bgm` のinstanceを取り出せるようになっている物なら何でも良く、
うまく使えば独自のキャッシュ戦略や読み込み戦略を採れるかもしれません。

.. [#hazudearu] 実際に測ったわけでは無いため
.. [#os_cache] OSのキャッシュが働けばその分は少しだけ早くなりうる
'''

__all__ = ('Bgm', 'BgmPlayer', 'CachedLoader', 'MemoryEfficientLoader', )

from collections import defaultdict
from kivy.event import EventDispatcher
from kivy.properties import BoundedNumericProperty
from kivy.core.audio import Sound, SoundLoader
import asynckivy as ak


class Bgm(EventDispatcher):
    '''一つ分のBGMの再生を司る下層のclass。'''

    length = BoundedNumericProperty(None, min=0.)
    '''
    (read-only) BGMの長さ。単位は秒。instance化直後はこの値はNoneなので実際の長さが入れられるまで少し待たないといけない。

    .. code-block::

       import asynckivy as ak

       bgm = Bgm(...)
       if bgm.length is None:
           await ak.event(bgm, 'length')
       print(f"BGMの長さは{bgm.length}秒です")
    '''

    fade_in_duration = BoundedNumericProperty(2., min=0.)
    '''何秒かけて音量を徐々に上げるか'''

    fade_out_duration = BoundedNumericProperty(2., min=0.)
    '''何秒かけて音量を徐々に下げるか'''

    volume = BoundedNumericProperty(1., min=0.)
    '''上げきった時の音量'''

    internal_delay = BoundedNumericProperty(.5, min=0.)
    ''':class:`kivy.core.audio.Sound` を操作する度に設ける内部用の待ち時間。'''

    def _get_pos(self):
        return self.sound.get_pos() if self._is_being_played else (self._pos or 0.)

    def _set_pos(self, new_pos):
        length = self.length
        if length is None:
            # 'length' is not available right now so setting 'pos' later
            self._pos = new_pos
            return
        sound = self.sound
        # normalize
        new_pos = (new_pos % length) if sound.loop else min(length, new_pos)
        self._pos = new_pos
        if self._is_being_played:
            sound.seek(new_pos)

    pos = property(_get_pos, _set_pos)
    '''再生位置。単位は秒。 :meth:`kivy.core.audio.Sound.seek` とは違って停止中にも自由に動かせる。'''

    def __init__(self, sound: Sound, **kwargs):
        self._pos = None
        self._needs_to_play = ak.Event()
        self._needs_to_stop = ak.Event()
        self.sound = sound
        self._is_at_max_volume = False

        self._is_being_played = False
        '''we need an own flag because `Sound.state` is not reliable'''

        super().__init__(**kwargs)
        self._main_task = ak.start(self._main())
        
    async def _main(self):
        from asynckivy import sleep, animate
        sound = self.sound
        needs_to_play = self._needs_to_play
        needs_to_stop = self._needs_to_stop
        try:
            self.length = await _get_sound_length(sound, self.internal_delay)
            self._set_pos(self._pos or 0.)
            while True:
                sound.volume = 0.
                await needs_to_play.wait()
                sound.play()
                await sleep(self.internal_delay)
                sound.seek(0 if self._reset_pos else self._pos)
                self._is_being_played = True
                await animate(sound, volume=self.volume, duration=self.fade_in_duration)
                sound.volume = self.volume
                self._is_at_max_volume = True
                await needs_to_stop.wait()
                self._is_at_max_volume = False
                await animate(sound, volume=0., duration=self.fade_out_duration)
                self._pos = sound.get_pos()
                self._is_being_played = False
                sound.stop()
                await sleep(self.internal_delay)
        finally:
            sound.unload()

    def on_volume(self, __, volume):
        if self._is_at_max_volume:
            self.sound.volume = volume

    def play(self, *, reset_pos=False):
        '''BGMを鳴らす。既定では前回の停止位置から再開するが ``reset_pos`` が真だと常に最初から鳴る。'''
        self._reset_pos = reset_pos
        self._needs_to_stop.clear()
        self._needs_to_play.set()

    def stop(self):
        '''BGMを停める'''
        self._needs_to_play.clear()
        self._needs_to_stop.set()

    def unload(self):
        ''' :meth:`kivy.core.audio.Sound.unload` を呼んで資源を解放する。以後はこのオブジェクトを操作しても何も起こらない。'''
        self._main_task.cancel()


async def _get_sound_length(sound: Sound, internal_delay):
    sound.volume = 0.
    sound.play()
    await ak.sleep(internal_delay)
    length = sound.length
    sound.stop()
    await ak.sleep(internal_delay)
    return length


class BgmPlayer(EventDispatcher):
    fade_in_duration = BoundedNumericProperty(2., min=0.)
    '''何秒かけて音量を徐々に上げるか'''

    fade_out_duration = BoundedNumericProperty(2., min=0.)
    '''何秒かけて音量を徐々に下げるか'''

    volume = BoundedNumericProperty(1., min=0.)
    '''上げきった時の音量'''

    internal_delay = BoundedNumericProperty(.5, min=0.)
    ''' :attr:`Bgm.internal_delay` '''

    def __init__(self, *, loader=None, **kwargs):
        self._needs_to_switch = ak.Event()
        self._cur_bgm = None
        if loader is None:
            loader = CachedLoader()
        super().__init__(**kwargs)
        self._main_task = ak.start(self._main(loader))

    async def _main(self, loader):
        needs_to_switch = self._needs_to_switch

        cur_key = None
        cur_bgm = None
        while True:
            await needs_to_switch.wait()
            needs_to_switch.clear()
            next_key, reset_pos = self._last_op
            has_key_changed = next_key != cur_key
            needs_to_stop = (self._cur_bgm is not None) and has_key_changed
            needs_to_load = has_key_changed and (next_key is not None)
            if needs_to_stop:
                self._cur_bgm = None
                cur_bgm.fade_out_duration = self.fade_out_duration
                cur_bgm.internal_delay = self.internal_delay
                cur_bgm.stop()
                await ak.sleep(cur_bgm.fade_out_duration + self.internal_delay)
                cur_bgm = None
                cur_key = None
            if needs_to_load:
                cur_bgm = loader[next_key]
                cur_bgm.volume = self.volume
                cur_key = next_key
                cur_bgm.fade_in_duration = self.fade_in_duration
                cur_bgm.internal_delay = self.internal_delay
                cur_bgm.play(reset_pos=reset_pos)
                await ak.sleep(cur_bgm.fade_in_duration + self.internal_delay)
                self._cur_bgm = cur_bgm
                cur_bgm.volume = self.volume

    def on_volume(self, __, volume):
        if self._cur_bgm is not None:
            self._cur_bgm.volume = volume

    def play(self, key, *, reset_pos=False):
        '''BGMを鳴らす。既定では前回の停止位置から再開するが ``reset_pos`` が真だと常に最初から鳴る。'''
        self._last_op = (key, reset_pos)
        self._needs_to_switch.set()

    def stop(self):
        '''BGMを停める'''
        self._last_op = (None, None)
        self._needs_to_switch.set()



class CachedLoader(dict):
    '''一度読み込んだBGMをずっと保持し続けるLoader'''

    def __missing__(self, filename):
        sound = SoundLoader.load(filename)
        sound.loop = True
        bgm = Bgm(sound)
        self[filename] = bgm
        return bgm


class MemoryEfficientLoader:
    '''BGM読み込み時に以前のBGMを破棄してメモリ使用量を抑えるLoader'''

    def __init__(self):
        self._last_filename = None
        self._last_bgm = None
        self._pos_dict = defaultdict(int)

    def __getitem__(self, filename):
        if self._last_filename == filename:
            return self._last_bgm
        if (last_bgm := self._last_bgm) is not None:
            self._pos_dict[self._last_filename] = last_bgm.pos
            last_bgm.unload()
        sound = SoundLoader.load(filename)
        sound.loop = True
        bgm = Bgm(sound)
        bgm.pos = self._pos_dict[filename]
        self._last_bgm = bgm
        self._last_filename = filename
        return bgm
