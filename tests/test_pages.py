import unittest

import pages


class TestMainPage(unittest.TestCase):
    def setUp(self):
        self.html = pages.render_main_page()

    def test_has_card_iframe_and_music(self):
        self.assertIn('<iframe src="/card"', self.html)
        self.assertIn('src="/music.wav"', self.html)
        self.assertIn("loop", self.html)

    def test_is_complete_html(self):
        self.assertTrue(self.html.startswith("<!doctype html>"))
        self.assertTrue(self.html.rstrip().endswith("</html>"))

    def test_no_leftover_format_markers(self):
        # catches mistakes with %% in the CSS templates
        self.assertNotIn("%%", self.html)
        self.assertNotIn("%%", pages.CARD_CSS)


class TestStars(unittest.TestCase):
    def test_five_star_buttons(self):
        html = pages.render_stars("Hello")
        for n in range(1, 6):
            self.assertIn(f'value="{n}"', html)
        self.assertEqual(html.count("&#9733;"), 5)

    def test_selected_stars_marked_on(self):
        html = pages.render_stars("Hello", selected=3)
        self.assertEqual(html.count("star on"), 3)

    def test_text_is_escaped(self):
        html = pages.render_stars('He said "hi" <b>')
        self.assertIn("&quot;hi&quot; &lt;b&gt;", html)
        self.assertNotIn("<b>", html)


class TestCard(unittest.TestCase):
    def test_placeholder_when_no_affirmation(self):
        html = pages.render_card()
        self.assertIn("placeholder", html)
        self.assertIn("Give me an affirmation", html)
        self.assertNotIn('action="/card/rate"', html)

    def test_shows_affirmation_rating_and_add_form(self):
        html = pages.render_card("I am enough.", average=4.25)
        self.assertIn("I am enough.", html)
        self.assertIn("Another affirmation", html)
        self.assertIn('action="/card/rate"', html)
        self.assertIn('action="/card/add"', html)
        self.assertIn("Average: 4.2", html)
        self.assertIn('name="prev" value="I am enough."', html)

    def test_unrated(self):
        self.assertIn("Not rated yet", pages.render_card("x"))

    def test_user_content_is_escaped(self):
        html = pages.render_card("<script>alert(1)</script>", message="<i>")
        self.assertNotIn("<script>", html)
        self.assertNotIn("<i>", html)

    def test_error_message_style(self):
        self.assertIn('class="message error"', pages.render_card(message="oops", error=True))


if __name__ == "__main__":
    unittest.main()
