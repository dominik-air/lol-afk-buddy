from kivy.app import App
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Line, Color
from os import listdir
from os.path import isfile, join
from abc import ABC, abstractmethod
from typing import List

# defines type hints and constants
RGBA = List[float]
BAN_COLOR = [1, 0, 0, 1]
PICK_COLOR = [0.2, 0.6, 1, 1]
DEFAULT_COLOR = [0.5, 0.5, 0.5, 1]

# loads the images' names into a list
images_path = "img/champion_images/"
images = [f for f in listdir(images_path) if isfile(join(images_path, f))]


class ChampionAction(ABC):
    @abstractmethod
    def action(self, champion_name: str, is_active: bool):
        pass


class BanChampion(ChampionAction):
    def action(self, champion_name: str, is_active: bool):
        if is_active:
            print(f"{champion_name} banned!")
        else:
            print(f"{champion_name} unbanned!")


class PickChampion(ChampionAction):
    def action(self, champion_name: str, is_active: bool):
        if is_active:
            print(f"{champion_name} picked!")
        else:
            print(f"{champion_name} unpicked!")


class ChampionButton(Button):
    border_color = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.border_color = DEFAULT_COLOR

    def set_default_border_color(self):
        self.border_color = DEFAULT_COLOR


class SearchBar(TextInput):
    def clear(self):
        self.text = ""


class ChampionArray(BoxLayout):
    champions = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.champions = []

        self._create_blank_array()

    def _create_blank_array(self, cols=5):
        for dummy_label in ["Dummy"] * cols:
            self.add_widget(Label(text=dummy_label))

    def add_champion(self, champion: ChampionButton):
        self.clear_widgets()
        self.champions.append(champion)
        for champion in self.champions:
            self.add_widget(Image(source=images_path + champion.text + ".png"))
        self._create_blank_array(cols=5 - len(self.champions))

    def remove_champion(self, champion: ChampionButton):
        self.clear_widgets()
        self.champions.remove(champion)
        for champion in self.champions:
            self.add_widget(Image(source=images_path + champion.text + ".png"))
        self._create_blank_array(cols=5 - len(self.champions))

    def clear(self):
        self.clear_widgets()
        for champion in self.champions:
            champion.set_default_border_color()
        self.champions = []
        self._create_blank_array()

    def contains(self, champion: ChampionButton) -> bool:
        return champion in self.champions


class ChampionArrayUI:
    def __init__(
        self,
        champion_action: ChampionAction,
        champion_array: ChampionArray,
        active_border_color: RGBA,
    ):
        self.champion_action = champion_action
        self.champion_array = champion_array
        self.active_border_color = active_border_color

    def action(self, champion: ChampionButton) -> None:
        if champion.border_color == self.active_border_color:
            champion.border_color = DEFAULT_COLOR
            self.champion_array.remove_champion(champion)
            self.champion_action.action(champion.text, is_active=False)
        else:
            champion.border_color = self.active_border_color
            self.champion_array.add_champion(champion)
            self.champion_action.action(champion.text, is_active=True)


class ChampionSelect(StackLayout):
    champion = ObjectProperty()
    champion_name = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.champion = ChampionButton(text="Dummy")
        self.champion_name = "Dummy"

        self.available_champions = []

        for image_name in images:
            champ = ChampionButton(
                text=image_name[:-4],
                font_size=0,
                size_hint=(None, None),
                size=(dp(42), dp(42)),
                background_normal=images_path + image_name,
                background_down=images_path + image_name,
            )

            champ.bind(on_press=self._set_champion)
            self.available_champions.append(champ)
            self.add_widget(champ)

    def _set_champion(self, new_champion: ChampionButton) -> None:
        self.champion = new_champion
        self.champion_name = new_champion.text

    def update_list(self, text: str):
        self.clear_widgets()
        if not text:
            for champion in self.available_champions:
                self.add_widget(champion)
        else:
            for champion in self.available_champions:
                if text in champion.text.lower():
                    self.add_widget(champion)


class ChampionSelectUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        ban_array_label = Label(
            text="Ban Priority Queue",
            font_size=20,
            size_hint=(1, 0.25),
            color=BAN_COLOR,
        )
        pick_array_label = Label(
            text="Pick Priority Queue",
            font_size=20,
            size_hint=(1, 0.25),
            color=PICK_COLOR,
        )
        ban_array = ChampionArray()
        pick_array = ChampionArray()

        self.add_widget(ban_array_label)
        self.add_widget(ban_array)
        self.add_widget(pick_array_label)
        self.add_widget(pick_array)

        self.banUI = ChampionArrayUI(
            champion_action=BanChampion(),
            champion_array=ban_array,
            active_border_color=BAN_COLOR,
        )
        self.pickUI = ChampionArrayUI(
            champion_action=PickChampion(),
            champion_array=pick_array,
            active_border_color=PICK_COLOR,
        )

    def ban_champion(self, champion):
        if self.pickUI.champion_array.contains(champion):
            self.pickUI.action(champion)
        self.banUI.action(champion)

    def pick_champion(self, champion):
        if self.banUI.champion_array.contains(champion):
            self.banUI.action(champion)
        self.pickUI.action(champion)

    def clear_bans(self):
        self.banUI.champion_array.clear()
        print("bans array cleared")

    def clear_picks(self):
        self.pickUI.champion_array.clear()
        print("picks array cleared")


class ChampionSelectInterface(BoxLayout):
    pass


class ChampionApp(App):
    def build(self):
        root_widget = ChampionSelectInterface()
        return root_widget


if __name__ == "__main__":
    ChampionApp().run()