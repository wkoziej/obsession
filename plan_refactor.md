⎿ Plan Refaktoryzacji Architektury Blender VSE

    Cel

    Zrefaktoryzować monolityczną klasę BlenderVSEConfigurator (892 linie) na mniejsze, bardziej skupione komponenty przy 
    zachowaniu pełnej kompatybilności wstecznej.

    Nowa Architektura

    1. Struktura Klas

    # src/core/blender_vse/constants.py
    class BlenderConstants:
        DEFAULT_FPS = 30
        DEFAULT_RESOLUTION_X = 1280
        DEFAULT_RESOLUTION_Y = 720
        
    class AnimationConstants:
        ENERGY_SCALE_FACTOR = 1.2
        PIP_SCALE_FACTOR = 1.1
        PIP_MARGIN = 120

    # src/core/blender_vse/config.py
    class BlenderVSEConfig:
        """Konfiguracja z walidacją parametrów"""
        
    # src/core/blender_vse/project_setup.py
    class BlenderProjectSetup:
        """Podstawowa konfiguracja projektu VSE"""
        
    # src/core/blender_vse/animation_engine.py
    class BlenderAnimationEngine:
        """Logika animacji z delegowaniem do specific animators"""
        
    # src/core/blender_vse/animators/
    class BeatSwitchAnimator:
    class EnergyPulseAnimator:
    class MultiPipAnimator:

    # src/core/blender_vse/layout_manager.py
    class BlenderLayoutManager:
        """Pozycjonowanie PiP i layout"""
        
    # src/core/blender_vse/keyframe_helper.py
    class KeyframeHelper:
        """Eliminacja duplikacji kodu keyframe'ów"""

    2. Zachowanie Kompatybilności

    - Główna klasa BlenderVSEConfigurator pozostaje jako facade
    - Wszystkie publiczne metody zachowują identyczne sygnatury
    - Zmienne środowiskowe pozostają bez zmian
    - Testy działają bez modyfikacji

    3. Kolejność Implementacji

    1. Faza 1: Utworzenie modułu constants i config
    2. Faza 2: Wyciągnięcie KeyframeHelper i LayoutManager
    3. Faza 3: Rozdzielenie animatorów na osobne klasy
    4. Faza 4: Refaktoryzacja głównej klasy jako facade
    5. Faza 5: Walidacja i testy
