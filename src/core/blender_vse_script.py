"""
Parametryczny skrypt Blender do konfiguracji VSE.

Ten skrypt może być uruchomiony w Blenderze i konfiguruje VSE project
na podstawie parametrów przekazanych przez zmienne środowiskowe.

Zmienne środowiskowe:
- BLENDER_VSE_VIDEO_FILES: Lista plików wideo (oddzielone przecinkami)
- BLENDER_VSE_MAIN_AUDIO: Ścieżka do głównego pliku audio
- BLENDER_VSE_OUTPUT_BLEND: Ścieżka do pliku .blend
- BLENDER_VSE_RENDER_OUTPUT: Ścieżka do pliku wyjściowego renderowania
- BLENDER_VSE_FPS: Liczba klatek na sekundę (domyślnie 30)
- BLENDER_VSE_RESOLUTION_X: Szerokość rozdzielczości (domyślnie 1280)
- BLENDER_VSE_RESOLUTION_Y: Wysokość rozdzielczości (domyślnie 720)

Użycie w Blenderze:
1. Otwórz Blender
2. Przejdź do workspace Scripting
3. Wklej ten skrypt
4. Ustaw zmienne środowiskowe lub zmodyfikuj parametry w skrypcie
5. Uruchom skrypt (Alt+P)

Użycie z CLI:
blender --background --python blender_vse_script.py
"""

import bpy
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple


class BlenderVSEConfigurator:
    """Konfigurator Blender VSE z parametrami."""

    def __init__(self):
        """Inicjalizuj konfigurator z parametrami z zmiennych środowiskowych."""
        self.video_files = self._parse_video_files()
        self.main_audio = self._get_env_path("BLENDER_VSE_MAIN_AUDIO")
        self.output_blend = self._get_env_path("BLENDER_VSE_OUTPUT_BLEND")
        self.render_output = self._get_env_path("BLENDER_VSE_RENDER_OUTPUT")
        self.fps = int(os.getenv("BLENDER_VSE_FPS", "30"))
        self.resolution_x = int(os.getenv("BLENDER_VSE_RESOLUTION_X", "1280"))
        self.resolution_y = int(os.getenv("BLENDER_VSE_RESOLUTION_Y", "720"))

    def _parse_video_files(self) -> List[Path]:
        """Parsuj listę plików wideo z zmiennej środowiskowej."""
        video_files_str = os.getenv("BLENDER_VSE_VIDEO_FILES", "")
        if not video_files_str:
            return []

        paths = []
        for path_str in video_files_str.split(","):
            path_str = path_str.strip()
            if path_str:
                paths.append(Path(path_str))
        return paths

    def _get_env_path(self, env_var: str) -> Optional[Path]:
        """Pobierz ścieżkę ze zmiennej środowiskowej."""
        path_str = os.getenv(env_var)
        return Path(path_str) if path_str else None

    def validate_parameters(self) -> Tuple[bool, List[str]]:
        """
        Waliduj parametry konfiguracji.

        Returns:
            Tuple[bool, List[str]]: (czy_valid, lista_błędów)
        """
        errors = []

        if not self.video_files:
            errors.append("Brak plików wideo (BLENDER_VSE_VIDEO_FILES)")

        for i, video_file in enumerate(self.video_files):
            if not video_file.exists():
                errors.append(f"Plik wideo {i + 1} nie istnieje: {video_file}")

        if self.main_audio and not self.main_audio.exists():
            errors.append(f"Główny plik audio nie istnieje: {self.main_audio}")

        if not self.output_blend:
            errors.append("Brak ścieżki wyjściowej .blend (BLENDER_VSE_OUTPUT_BLEND)")

        if not self.render_output:
            errors.append("Brak ścieżki renderowania (BLENDER_VSE_RENDER_OUTPUT)")

        if self.fps <= 0:
            errors.append(f"Nieprawidłowa wartość FPS: {self.fps}")

        if self.resolution_x <= 0 or self.resolution_y <= 0:
            errors.append(
                f"Nieprawidłowa rozdzielczość: {self.resolution_x}x{self.resolution_y}"
            )

        return len(errors) == 0, errors

    def setup_vse_project(self) -> bool:
        """
        Skonfiguruj projekt Blender VSE.

        Returns:
            bool: True jeśli sukces
        """
        print("=== Konfiguracja projektu Blender VSE ===")

        # Walidacja parametrów
        is_valid, errors = self.validate_parameters()
        if not is_valid:
            print("✗ Błędy walidacji parametrów:")
            for error in errors:
                print(f"  - {error}")
            return False

        try:
            # 1. Wyczyść domyślną scenę
            bpy.ops.wm.read_factory_settings(use_empty=True)
            print("✓ Wyczyszczono domyślną scenę")

            # 2. Utwórz sequence editor
            if not bpy.context.scene.sequence_editor:
                bpy.context.scene.sequence_editor_create()
            print("✓ Utworzono sequence editor")

            # 3. Skonfiguruj podstawowe ustawienia sceny
            scene = bpy.context.scene
            scene.render.resolution_x = self.resolution_x
            scene.render.resolution_y = self.resolution_y
            scene.render.fps = self.fps
            scene.frame_start = 1
            print(
                f"✓ Ustawiono podstawowe parametry sceny ({self.resolution_x}x{self.resolution_y}, {self.fps}fps)"
            )

            # 4. Dodaj główny pasek audio (kanał 1)
            sequencer = scene.sequence_editor

            if self.main_audio:
                try:
                    sequencer.sequences.new_sound(
                        name="Main_Audio",
                        filepath=str(self.main_audio),
                        channel=1,  # Kanał audio 1
                        frame_start=1,
                    )
                    print(
                        f"✓ Dodano główne audio: {self.main_audio.name} (kanał audio 1)"
                    )
                except Exception as e:
                    print(f"✗ Błąd dodawania głównego audio: {e}")
                    return False

            # 5. Dodaj paski wideo do kanałów (zaczynając od kanału 2)
            for i, video_file in enumerate(self.video_files):
                try:
                    # Dodaj pasek wideo do kanału (i + 2) - zaczynamy od kanału 2
                    channel = i + 2
                    sequencer.sequences.new_movie(
                        name=f"Video_{i + 1}",
                        filepath=str(video_file),
                        channel=channel,
                        frame_start=1,
                    )
                    print(
                        f"✓ Dodano pasek wideo {i + 1}: {video_file.name} (kanał {channel})"
                    )
                except Exception as e:
                    print(f"✗ Błąd dodawania wideo {video_file}: {e}")
                    return False

            # 6. Skonfiguruj ustawienia renderowania
            render = scene.render
            render.image_settings.file_format = "FFMPEG"
            render.ffmpeg.format = "MPEG4"
            render.ffmpeg.codec = "H264"
            render.ffmpeg.constant_rate_factor = "HIGH"
            render.filepath = str(self.render_output)
            print("✓ Skonfigurowano ustawienia renderowania (MP4, H.264)")

            # 7. Ustaw timeline aby pokazać całą zawartość
            if sequencer.sequences:
                # Znajdź najdłuższą sekwencję
                max_frame_end = max(seq.frame_final_end for seq in sequencer.sequences)
                scene.frame_end = max_frame_end
                print(f"✓ Ustawiono koniec timeline na klatkę {max_frame_end}")

            # 8. Zapisz plik .blend
            if self.output_blend:
                try:
                    # Upewnij się, że katalog istnieje
                    self.output_blend.parent.mkdir(parents=True, exist_ok=True)
                    bpy.ops.wm.save_as_mainfile(filepath=str(self.output_blend))
                    print(f"✓ Zapisano projekt: {self.output_blend}")
                except Exception as e:
                    print(f"✗ Błąd zapisywania projektu: {e}")
                    return False

            print("=== Konfiguracja projektu VSE zakończona sukcesem ===")
            return True

        except Exception as e:
            print(f"✗ Błąd krytyczny: {e}")
            import traceback

            traceback.print_exc()
            return False


def main() -> int:
    """
    Główna funkcja skryptu.

    Returns:
        int: Kod wyjścia (0 dla sukcesu, 1 dla błędu)
    """
    configurator = BlenderVSEConfigurator()

    print("=== Parametryczny skrypt Blender VSE ===")
    print(f"Pliki wideo: {len(configurator.video_files)}")
    print(f"Główne audio: {configurator.main_audio}")
    print(f"Plik wyjściowy: {configurator.output_blend}")
    print(f"Renderowanie: {configurator.render_output}")
    print(f"Rozdzielczość: {configurator.resolution_x}x{configurator.resolution_y}")
    print(f"FPS: {configurator.fps}")
    print()

    success = configurator.setup_vse_project()

    if success:
        print("✅ Projekt VSE skonfigurowany pomyślnie!")
        return 0
    else:
        print("❌ Błąd konfiguracji projektu VSE")
        return 1


# Sprawdź czy jesteśmy w Blenderze czy uruchamiamy z linii poleceń
def is_running_in_blender() -> bool:
    """Sprawdź czy skrypt jest uruchamiany w Blenderze."""
    try:
        import importlib.util

        spec = importlib.util.find_spec("bpy")
        return spec is not None
    except ImportError:
        return False


# Uruchom główną funkcję tylko gdy skrypt jest wykonywany bezpośrednio
if __name__ == "__main__":
    exit_code = main()

    # Jeśli uruchamiamy z linii poleceń (nie w Blenderze), użyj sys.exit()
    if not is_running_in_blender():
        sys.exit(exit_code)
