# Poprawki po review — grpc-workshop

Kontekst: to repo warsztatowe. Uczestnicy przechodzą ćwiczenia 01–07 krok po kroku i uczą się gRPC.
Każda zmiana ma ułatwiać naukę: jasne instrukcje, prawdziwe komunikaty błędów, testy sprawdzające pracę uczestnika.

## Zasady pracy

- Rób **jedno zadanie naraz**, w kolejności z listy. Po każdym zadaniu pokaż diff i poczekaj na akceptację.
- Nie implementuj rozwiązań w plikach startowych uczestnika (`exercises/server.py`, `*_starter.py`, `07_final_chat_client/client.py`) — mają zostać z TODO.
- Treść ćwiczeń jest zduplikowana: główny `README.md` (sekcje „Exercise N”) **i** `workshop/exercises/0N_*/README.md`. Każdą zmianę treści nanoś w obu miejscach.
- Weryfikacja po każdym zadaniu (z katalogu `workshop/`):
  - `uv run poe test-exercises` na czystym repo → oczekiwany wynik startowy (dziś: 25 failed, 4 passed; jeśli zmienisz testy, zaktualizuj liczby w README).
  - Test rozwiązań: w kopii repo wklej rozwiązania z README (bloki „Click to view Solution N”) + serwer z ćw. 5 → wszystkie testy mają przejść.
- Weryfikacja Dockera — uruchamiaj po każdym zadaniu, które dotyka `infrastructure/`, `docker-compose.yml`, `pyproject.toml`, `.python-version` lub instrukcji uruchamiania w README, oraz zawsze na koniec sekcji A:
  ```bash
  docker compose build
  docker compose run --rm workshop python --version          # ma się zgadzać z .python-version
  docker compose run --rm workshop poe test-exercises        # ten sam wynik co lokalnie
  docker compose up -d server                                # poczekaj, aż będzie "healthy": docker compose ps
  docker compose run --rm workshop poe client-send --host server "Hello"   # na czystym repo: błąd INTERNAL to OK
  docker compose exec server uv run poe starter-04           # sprawdza ścieżkę z pkt 3
  docker compose down
  ```
  Zapisz faktyczne wyniki. Jeśli jakaś komenda z README nie działa w Dockerze, popraw README, a nie tylko konfigurację.
- Jeśli któryś punkt z tej listy okaże się nieprawdziwy albo poprawka byłaby gorsza niż obecny stan — **zatrzymaj się i napisz dlaczego**, nie poprawiaj na siłę.
- Nie zmieniaj bez pytania nazw rzeczy, na których opiera się uczestnik: zadań `poe`, ścieżek plików ćwiczeń, nazw klas i metod w `chat.proto`.
- Treść repo (README, komentarze, docstringi) zostaje po angielsku.
- Nie ruszaj `assets/` ani `uv.lock` ręcznie (lock tylko przez `uv lock`, jeśli zmieniasz zależności).

## A. Rzeczy, które blokują uczestnika

1. **Zły import w rozwiązaniach 6 i 7.** W `README.md` (Solution 6 i Solution 7) jest `from solutions.generated import ...` — pakiet `solutions` nie istnieje, kopiowanie rozwiązania 7 psuje zbieranie wszystkich testów (`ModuleNotFoundError`). Zmień na `from exercises.generated import ...`. W Solution 6 zmień też nazwę `SOLUTION_SERVER` na `EXERCISE_SERVER` (zgodnie ze starterem).
2. **Resztki po katalogu `solutions/`.** Usuń/popraw:
   - `pyproject.toml`: `testpaths` (usuń `tests/solutions`), `[tool.hatch.build.targets.wheel] packages` (usuń `solutions`),
   - `infrastructure/entrypoint.sh`: linia `generate "solutions/..."`,
   - `docker-compose.yml`: komentarz z `poe test-solutions`,
   - docstring w Solution 5 (`python solutions/05_streaming/streaming.py` → `poe starter-05`).
3. **Startery w Dockerze nie łączą się z serwerem.** `starter-04/05/06` mają na sztywno `localhost:50051`, a `docker compose run` startuje osobny kontener. W README (sekcja „How to prepare for the workshop”) i w README ćwiczeń 4–6 dodaj ścieżkę dockerową:
   `docker compose up server` (terminal 1) oraz `docker compose exec server uv run poe starter-04` (terminal 2). Uwaga: `exec` pomija entrypoint, a venv jest w `/opt/venv` poza `PATH`, więc samo `poe` nie zadziała — potrzebne `uv run`. Sprawdź to na żywym Dockerze. Analogicznie dla `client-*` (zamiast ukrytej opcji `--host server`).
4. **`poe server` nie regeneruje kodu po zmianie `.proto`.** W `pyproject.toml` zadanie `server` generuje tylko, gdy brakuje pliku. Zmień tak, aby zawsze uruchamiało `poe generate-exercises` przed startem.
5. **`entrypoint.sh` duplikuje generację i ukrywa błędy** (brak stubów mypy, `2>/dev/null || true`). Zastąp całą funkcję `generate` wywołaniem `uv run poe generate-exercises` (błąd ma być widoczny, ale nie blokować startu `bash`).
6. **Pułapka w podpowiedzi do ćw. 5 (Task 2).** Snippet `_store.setdefault(request.room_id, []).append(...)` wkleja `Ellipsis` do store i psuje `GetHistory`. Zamień na `_make_message(request)`.
7. **Brak sposobu na nadrobienie zaległości.** Dodaj do README ćw. 5 rozwiązanie z kompletnym `server.py` (wszystkie 4 metody), aby uczestnik, który utknął, mógł wkleić jeden plik i iść dalej.

## B. Rzeczy, które uczą nieprawdy

8. **Zły status dla metody z `pass` (ćw. 2 i 3).** Sprawdzone: unary z `pass` → `INTERNAL` („Failed to serialize response!”), streaming z `pass` → `UNKNOWN`. `UNIMPLEMENTED` jest tylko, gdy metody w ogóle nie zdefiniowano. Popraw sekcje „Micro-check” w ćw. 2 i 3 i krótko wyjaśnij różnicę (to dobra lekcja o statusach).
9. **Spoiler ćw. 7.** `exercises/client.py` zawiera gotowe rozwiązanie ćw. 7, a instrukcja „Copy client.py from 07_final_chat_client/ to exercises/” wykonana za wcześnie psuje `poe client-*`. Zaproponuj rozwiązanie (np. osobne zadania `poe final-send/final-history/final-chat` uruchamiające `07_final_chat_client/client.py`, a `exercises/client.py` zostaje jako narzędzie do smoke testów z ćw. 3–5) i usuń instrukcję kopiowania. Przedstaw propozycję przed wdrożeniem.
10. **Testy przechodzą bez pracy uczestnika:**
    - `tests/exercises/test_04_unary_client.py` testuje serwer, nie `exercises/04_unary_client/client_starter.py` → dodaj test, który uruchamia `main()` startera (port przez parametr/zmienną albo monkeypatch) i sprawdza wypisane `message_id`/`status`,
    - `test_05_streaming.py` — dodaj testy funkcji `demo_*` ze `streaming_starter.py`,
    - `test_06_...` — test deadline sprawdza bibliotekę grpc; zamień na test `demo_deadline_exceeded()` / `demo_invalid_argument()` ze startera (np. przez `capsys`),
    - `test_01_proto.py` — dodaj test `BulkResponse`.
    Startery są skryptami w katalogach z cyframi — ładuj je przez `importlib.util.spec_from_file_location` (jak w `test_07`). Zaktualizuj w README oczekiwaną liczbę failed/passed.
11. **Nazwy ćwiczeń vs treść.** Ćw. 5 mówi „Extend the server with all four communication patterns”, a dodaje trzy (unary jest z ćw. 3) — doprecyzuj zdanie, np. „complete all four patterns by adding the three streaming ones”. Ćw. 6 ma w nazwie katalogu „cancellation”, ale tego nie uczy — dodaj krótki bonus albo zmień opis. Bonus: po stronie klienta wywołanie strumieniowe zwraca obiekt z `.cancel()` (`call = stub.GetHistory(...)`, potem `call.cancel()`; `.future()` istnieje tylko dla unary), po stronie serwera `context.is_active()` / `context.add_callback(...)`.

## C. Ergonomia warsztatu

12. **Testy per ćwiczenie:** zadania `poe test-01` … `poe test-07` (każde generuje kod i uruchamia jeden plik testów). Opisz je w README każdego ćwiczenia w sekcji „Verify”.
13. **Restart serwera:** w ćw. 3 i 5 dopisz, że po zmianie `server.py` trzeba zrestartować `poe server`, a store w pamięci jest wtedy czyszczony (historia znika).
14. **Sekcja „Common mistakes / Troubleshooting”** w głównym README: port zajęty (`Address already in use`), brak wygenerowanego kodu, zmiana `.proto` bez regeneracji, zła nazwa pokoju, `messages` zamiast `messages()`, Docker i `localhost`.
15. **Szacowany czas** przy każdym ćwiczeniu + oznaczenie, co jest bonusem.
16. **Porządki:** pusty `workshop/README.md` (wypełnij krótkim opisem z linkiem do głównego README), zduplikowana sekcja „Project Setup” i podwójny nagłówek „Exercise 7” w głównym README, `.python-version` (3.13) vs `python:3.12-slim` w Dockerfile — ujednolić, przypiąć wersję obrazu uv, `ruff`: dodać `exclude = ["exercises/generated"]` i naprawić pozostałe błędy, usunąć nieużywany import `StatusCode`… tylko jeśli nie jest potrzebny w TODO dla ćw. 3 (jest — zostaw, dodaj `# noqa: F401` z komentarzem).

## D. Nowe materiały (osobno, po A–C — najpierw zaproponuj plan)

17. **Finał: prawdziwy czat** — wiadomości z `Chat` rozsyłane do wszystkich klientów w pokoju (kolejka na subskrybenta, sprzątanie przez `context.add_callback`). Demo: dwa terminale, alice i bob.
18. **Omówienie wygenerowanego `chat_pb2_grpc.py`** (Stub, Servicer, `add_..._to_server`) w ćw. 2.
19. **Domyślne wartości proto3** (`limit = 0` = „nie podano”) — notka w ćw. 1/5.
20. **grpcurl + reflection** (`grpcio-reflection` już jest w zależnościach) — bonus po ćw. 3.
21. **Ewolucja kontraktu** — dodanie pola do `Message`, stary klient dalej działa; `reserved`.
22. **Metadata + interceptor** (token / request-id) — bonus.
23. **Walidacja w `SendBulkMessages`** — liczenie `messages_failed` dla pustych treści.
24. **CI (GitHub Actions)** — job 1: czyste repo daje oczekiwany wynik testów; job 2: wklejone rozwiązania z README → wszystkie testy zielone (wyłapie błędy typu z pkt 1).

## E. Znalezione przy przejściu ćwiczeń jak uczestnik

Przejście 01–07 na czystym repo (tylko instrukcje i podpowiedzi, bez bloków „Click to view Solution”).
Wynik końcowy: wszystkie 29 testów przechodzi, więc ścieżka jako całość **działa**. Poniżej to, co po drodze myli lub blokuje.

25. **Pułapka z pkt 6 nie jest łapana przez testy — i psuje ćwiczenie po cichu.**
    Po wklejeniu podpowiedzi z ćw. 5 Task 2 *dosłownie* (`append(...)`) `poe test-exercises` daje
    komplet zielonych testów 01–06, bo każdy test używa własnego pokoju. Ale w realnym użyciu:
    `SendBulkMessages` do pokoju `general` zwraca `messages_sent: 3`, a następne
    `GetHistory(general)` wywala się na `INTERNAL: Failed to serialize response!`.
    Uczestnik dostaje więc „wszystko zielone”, a aplikacja jest zepsuta.
    Przy poprawianiu pkt 6 warto dodać test, który robi bulk i history **do tego samego pokoju** —
    inaczej ta sama pułapka wróci przy kolejnej edycji README.

26. **Micro-check ćw. 2 mówi „unimplemented”, a uczestnik widzi `INTERNAL`.**
    README ćw. 2: „If it prints `unimplemented` when you call it, the stub is wired correctly”.
    Faktycznie po dodaniu czterech metod z `pass` i wywołaniu `poe client-send` jest:
    `✗ StatusCode.INTERNAL: Failed to serialize response!`.
    To ten sam problem co pkt 8, ale warto odnotować, że dotyczy **obu** zdań w ćw. 2
    (i „unimplemented”, i opisu w ćw. 3), oraz że zmierzone wartości to:
    | stan servicera | unary | streaming |
    |---|---|---|
    | metoda z `pass` | `INTERNAL: Failed to serialize response!` | `UNKNOWN: Exception iterating responses: 'NoneType' object is not an iterator` |
    | metody brak | `UNIMPLEMENTED: Method not implemented!` | `UNIMPLEMENTED: Method not implemented!` |

27. **Brak `poe client-bulk` — `SendBulkMessages` nie da się sprawdzić z CLI.**
    Sekcja „Test it” w ćw. 5 pokazuje `client-send`, `client-history` i `client-chat`,
    ale dla client-streamingu nie ma odpowiednika. Jedyny sposób to `poe starter-05`,
    co miesza dwie rzeczy (własne eksperymenty uczestnika i smoke test serwera).
    Propozycja: dodać `poe client-bulk --room general --count 5` do `exercises/client.py`.

28. **`poe starter-05` wywala się na pierwszym TODO i nie pokazuje reszty.**
    Starter woła po kolei `demo_unary`, `demo_server_streaming`, `demo_client_streaming`,
    `demo_bidirectional`. Dopóki uczestnik nie napisze `demo_client_streaming`,
    `messages()` zwraca `None` → `TypeError` przerywa cały skrypt i `demo_bidirectional`
    nigdy się nie uruchamia. Warto albo owinąć każde demo w `try/except` z czytelnym
    „[not implemented yet]”, albo wspomnieć w README, że demo komentuje się po kolei.

29. **Ćw. 4: instrukcja mówi „Try sending an empty message”, ale starter nie ma jak.**
    `client_starter.py` ma treść zahardkodowaną w `main()`, więc żeby spróbować pustej
    wiadomości, trzeba edytować plik — README tego nie mówi. Albo dodać zdanie
    („zmień `content` na `""` i uruchom ponownie”), albo dać `main(content: str = "...")`.

30. **Nie ma informacji, że `poe server` trzeba zrestartować po każdej zmianie `server.py`.**
    To pokrywa pkt 13, ale potwierdzam z praktyki: przy ćw. 5 bardzo łatwo zaimplementować
    `GetHistory`, odpytać działający od ćw. 3 serwer i dostać `UNIMPLEMENTED`,
    nie rozumiejąc dlaczego. To najbardziej prawdopodobne miejsce na zacięcie się grupy.

31. **`ruff check .` na czystym repo zwraca 37 błędów.**
    Większość to wygenerowany `exercises/generated/` (stąd `exclude` z pkt 16),
    ale są też prawdziwe w plikach warsztatowych, m.in. `W293` (whitespace w pustych liniach)
    w `tests/exercises/test_06_deadlines_cancellation_errors.py` i `E402`/`W291` gdzie indziej.
    Uczestnik, który odruchowo odpali `poe lint`, zobaczy ścianę błędów niezwiązanych z jego pracą.

32. **Docker: `python --version` pokazuje 3.13.18, mimo `python:3.12-slim` w Dockerfile.**
    `uv sync` respektuje `.python-version` (3.13) i ściąga własny interpreter, więc tag obrazu
    bazowego jest mylący, a nie faktycznie używany. Potwierdza pkt 16 i wskazuje kierunek:
    ujednolicić na 3.13 (obraz + `.python-version`), żeby nie sugerować, że warsztat działa na 3.12.

33. **Potwierdzenie pkt 4 na żywo.** Po dopisaniu nowej wiadomości do `chat.proto` i `poe server`
    nowy typ **nie** jest widoczny w `exercises.generated` — zadanie `server` pomija generację,
    bo plik już istnieje. Żadnego ostrzeżenia; wygląda to jak błąd w kodzie uczestnika.

34. **Nieaktualne w pkt 16: nie ma podwójnego nagłówka „Exercise 7”.**
    W `README.md` jest tylko jeden (`# Exercise 7: Final Chat Client in \`client.py\``, linia 1695).
    Zduplikowana sekcja „Project Setup” (linie 4 i 643) — owszem, jest.

## F. Znalezione przy powtórnym przejściu (na branchu z poprawkami)

35. **`ruff --fix` (z pkt 16) usunął ze starterów importy potrzebne do TODO.**
    `ruff` uznał `chat_pb2` za nieużywany w `deadlines_starter.py` i w
    `07_final_chat_client/client.py` — bo w kodzie startowym faktycznie jeszcze
    nie jest użyty. Uczestnik wypełniający TODO zgodnie z instrukcją dostawał
    `NameError: name 'chat_pb2' is not defined`.
    Naprawione: importy przywrócone, a startery mają `F401` w
    `[tool.ruff.lint.per-file-ignores]`, żeby kolejne `ruff --fix` ich nie zjadło.
    Wniosek na przyszłość: **nie puszczać `ruff --fix` na pliki startowe** —
    to, co wygląda tam na martwy kod, jest treścią ćwiczenia.
