from .. import register_command


@register_command("test")
def test_command():
    print("Hello, world")
