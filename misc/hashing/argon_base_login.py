import argon2

# Passwort hashen
def hash_password(password):
    ph = argon2.PasswordHasher()
    return ph.hash(password)

# Passwort überprüfen
def verify_password(hashed_password, password_to_check):
    ph = argon2.PasswordHasher()
    try:
        ph.verify(hashed_password, password_to_check)
        return True  # Passwort ist korrekt
    except:
        return False  # Passwort ist falsch

# Beispiel: Benutzer registrieren
password = "test"

hashed_password = hash_password(password)
print("Passwort erfolgreich gehasht:", hashed_password)

# Beispiel: Benutzeranmeldung
login_password = "test"  # Ändern Sie dies in das richtige Passwort, um die Anmeldung erfolgreich zu testen
if verify_password(hashed_password, login_password):
    print("Anmeldung erfolgreich.")
else:
    print("Falsches Passwort.")


