"""
Script para hacer clic en los corazones (favoritos) de los anuncios
en biella.mercatinousato.com - páginas 1 a 6

Flujo:
  1. Abre la página principal
  2. Hace clic en el botón "login" (abre overlay JS)
  3. Rellena email y contraseña y hace clic en "Accedi"
  4. Verifica que el login fue correcto
  5. Recorre páginas 1-6 haciendo clic en todos los corazones

Selector corazones: img.product-wishlist
  - add-wishlist     → pendiente, se hace clic
  - no-wishlist-click → ya en favoritos, se salta
"""

import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    ElementNotInteractableException,
    TimeoutException,
    StaleElementReferenceException
)

# ── Credenciales ──────────────────────────────────────────────
EMAIL      = "e220689@gmail.com"
PASSWORD   = "Edgar123"

# ── Configuración ─────────────────────────────────────────────
BASE_URL    = "https://biella.mercatinousato.com/prodotti/tutti"
TOTAL_PAGES = 6


def build_page_url(page: int) -> str:
    if page == 1:
        return f"{BASE_URL}?tutti=1"
    return f"{BASE_URL}/pageno/{page}"


def setup_driver(headless: bool = False) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


def accept_cookies(driver: webdriver.Chrome) -> None:
    """Acepta el banner de cookies si aparece."""
    try:
        btn = WebDriverWait(driver, 6).until(
            EC.element_to_be_clickable((By.XPATH,
                "//button[contains(text(),'Accetta') or contains(text(),'OK') "
                "or contains(text(),'Accetto') or contains(text(),'Acconsento')]"
            ))
        )
        btn.click()
        print("  -> Cookie banner aceptado.")
        time.sleep(1)
    except TimeoutException:
        pass


def type_slowly(element, text: str) -> None:
    """Escribe texto carácter a carácter para simular escritura humana."""
    element.clear()
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))


def do_login(driver: webdriver.Chrome) -> bool:
    """
    Realiza el login completo:
      1. Clic en botón 'login' del header (abre overlay JS)
      2. Rellena email y contraseña
      3. Clic en 'Accedi'
      4. Verifica login correcto
    Devuelve True si el login fue exitoso.
    """
    print("\n" + "="*55)
    print("  INICIO DE SESION")
    print("="*55)

    # Cargar la página principal
    driver.get(f"{BASE_URL}?tutti=1")
    time.sleep(random.uniform(2, 3))
    accept_cookies(driver)

    # ── Paso 1: clic en el botón login del header ─────────────
    print("  -> Buscando botón de login...")
    try:
        # Hay varios botones .btnaccedi, usamos el del header principal
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "aqHeader_hypLogin"))
        )
        login_btn.click()
        print("  -> Botón login clickeado, esperando overlay...")
    except TimeoutException:
        # Fallback: cualquier enlace con clase btnaccedi
        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "a.btnaccedi")
            driver.execute_script("arguments[0].click();", login_btn)
            print("  -> Botón login (fallback) clickeado.")
        except Exception as e:
            print(f"  XX No se encontró el botón de login: {e}")
            return False

    # ── Paso 2: esperar que aparezca el overlay de login ──────
    try:
        email_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "aqLogin_txtEmail_req"))
        )
        print("  -> Overlay de login visible.")
    except TimeoutException:
        print("  XX Timeout esperando el overlay de login.")
        return False

    time.sleep(0.5)

    # ── Paso 3: rellenar email ────────────────────────────────
    print(f"  -> Escribiendo email: {EMAIL}")
    # El campo usa placeholder como value, hay que limpiar antes
    driver.execute_script("arguments[0].value = '';", email_field)
    email_field.click()
    time.sleep(0.3)
    type_slowly(email_field, EMAIL)

    # ── Paso 4: rellenar contraseña ───────────────────────────
    print("  -> Escribiendo contraseña...")
    try:
        pwd_field = driver.find_element(By.ID, "aqLogin_txtPassword_req")
        driver.execute_script("arguments[0].value = '';", pwd_field)
        pwd_field.click()
        time.sleep(0.3)
        type_slowly(pwd_field, PASSWORD)
    except Exception as e:
        print(f"  XX No se encontró el campo de contraseña: {e}")
        return False

    time.sleep(0.5)

    # ── Paso 5: clic en "Accedi" ──────────────────────────────
    print("  -> Haciendo clic en 'Accedi'...")
    try:
        accedi_btn = driver.find_element(By.ID, "aqLogin_hypAccedi")
        accedi_btn.click()
    except Exception as e:
        print(f"  XX No se encontró el botón Accedi: {e}")
        return False

    # ── Paso 6: verificar login exitoso ───────────────────────
    print("  -> Verificando login...")
    time.sleep(3)

    try:
        # Si el login fue bien, el botón logout se hace visible
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "a.btnlogout"))
        )
        print("  OK LOGIN CORRECTO - Sesion iniciada.")
        return True
    except TimeoutException:
        # Comprobar si hay mensaje de error
        try:
            err = driver.find_element(By.CSS_SELECTOR, "span.mess-errore")
            if err.is_displayed():
                print("  XX LOGIN FALLIDO: email o contraseña incorrectos.")
                return False
        except Exception:
            pass
        print("  ?? No se pudo confirmar el login, continuando de todas formas...")
        return True  # Intentar continuar


def scroll_page(driver: webdriver.Chrome) -> None:
    """Scroll suave para cargar todos los elementos lazy."""
    total_height = driver.execute_script("return document.body.scrollHeight")
    for pos in range(0, total_height, 400):
        driver.execute_script(f"window.scrollTo(0, {pos});")
        time.sleep(0.05)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.5)


def click_hearts_on_page(driver: webdriver.Chrome, page: int):
    """
    Hace clic en todos los corazones pendientes de la pagina.
    Devuelve (clickeados, ya_añadidos).
    """
    url = build_page_url(page)
    print(f"\n{'='*55}")
    print(f"  Pagina {page}: {url}")
    print('='*55)

    driver.get(url)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img.product-wishlist"))
        )
    except TimeoutException:
        print("  AVISO: Timeout, no se encontraron corazones en la pagina.")
        return 0, 0

    time.sleep(random.uniform(1.5, 2.5))
    scroll_page(driver)

    hearts = driver.find_elements(By.CSS_SELECTOR, "img.product-wishlist")
    total = len(hearts)
    print(f"  -> {total} corazones encontrados en la pagina.")

    clicked    = 0
    ya_añadido = 0

    for i, heart in enumerate(hearts, 1):
        try:
            classes = heart.get_attribute("class") or ""
            id_prod = heart.get_attribute("data-idprodotto") or "?"

            if "no-wishlist-click" in classes:
                ya_añadido += 1
                print(f"  >> [{i:02d}/{total}] Producto {id_prod} ya esta en favoritos, saltando.")
                continue

            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", heart
            )
            time.sleep(0.4)

            try:
                heart.click()
            except ElementNotInteractableException:
                driver.execute_script("arguments[0].click();", heart)

            clicked += 1
            print(f"  OK [{i:02d}/{total}] Corazon clickeado - producto {id_prod}")
            time.sleep(random.uniform(0.6, 1.4))

        except StaleElementReferenceException:
            print(f"  !! [{i:02d}/{total}] Elemento obsoleto (StaleElement), saltando.")
        except Exception as e:
            print(f"  XX [{i:02d}/{total}] Error: {e}")

    print(f"\n  Pagina {page} terminada -> Clickeados: {clicked} | Ya en favoritos: {ya_añadido} | Total: {total}")
    return clicked, ya_añadido


def main():
    print("Script de corazones - mercatinousato Biella")
    print(f"Procesando paginas 1 a {TOTAL_PAGES}\n")

    # Cambia headless=True para ejecutar sin ventana del navegador
    driver = setup_driver(headless=False)

    total_clicked    = 0
    total_ya_añadido = 0

    try:
        # ── LOGIN ─────────────────────────────────────────────
        login_ok = do_login(driver)
        if not login_ok:
            print("\nXX No se pudo iniciar sesion. Abortando.")
            driver.quit()
            return

        time.sleep(2)

        # ── RECORRER PAGINAS ──────────────────────────────────
        for page in range(1, TOTAL_PAGES + 1):
            n_click, n_ya = click_hearts_on_page(driver, page)
            total_clicked    += n_click
            total_ya_añadido += n_ya

            if page < TOTAL_PAGES:
                wait = random.uniform(3, 6)
                print(f"\n  Esperando {wait:.1f}s antes de la pagina {page + 1}...")
                time.sleep(wait)

    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario.")
    finally:
        driver.quit()

    print(f"\n{'='*55}")
    print(f"PROCESO COMPLETADO")
    print(f"  Corazones clickeados:    {total_clicked}")
    print(f"  Ya estaban en favoritos: {total_ya_añadido}")
    print(f"{'='*55}")


if __name__ == "__main__":
    main()