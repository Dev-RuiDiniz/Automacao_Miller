from getpass import getpass

from .app import hash_password


def main() -> None:
    password = getpass("Senha da landing: ")
    confirmation = getpass("Confirme a senha: ")
    if not password or password != confirmation:
        raise SystemExit("As senhas não coincidem ou estão vazias.")
    print(hash_password(password))


if __name__ == "__main__":
    main()
