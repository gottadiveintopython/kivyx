def test():
    from kivy.resources import resource_find
    from kivyx.utils import register_assets_just_for_testing
    register_assets_just_for_testing()
    assert resource_find(r'assets_just_for_testing/nothing_other_than_test')
