use argon2::password_hash::rand_core::OsRng;
use argon2::password_hash::SaltString;
use argon2::{Argon2, PasswordHash, PasswordHasher, PasswordVerifier};

pub struct Crypt;

impl Crypt {
    pub fn verify_password(stored_password: &str, entered_password: &String) -> bool {
        let hash = PasswordHash::new(stored_password).unwrap();

        let password: &[u8] = entered_password.as_bytes();

        Argon2::default().verify_password(password, &hash).is_ok()
    }

    pub fn hash_password(plain_password: &str) -> String {
        let argon2 = Argon2::default();
        let salt = SaltString::generate(&mut OsRng);

        let hashed_password = argon2.hash_password(plain_password.as_bytes(), &salt).unwrap();
        hashed_password.to_string()
    }    
}
