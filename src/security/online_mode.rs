use reqwest::Client;
use crate::global::{API, LOGGER};


#[derive(Default)]
pub struct OnlineMode {
    pub enabled: bool,
    pub server_uuid: String,
    pub server_ip: String,
}

impl OnlineMode {
    pub fn new() -> Self {
        Self::default()
    }

    pub async fn auth(&self) {
        if self.enabled {
            let client = Client::new();

            let Ok(response) = client.get(format!("{API}utils/user/ip")).send().await else { return };

            if response.status().is_success() {
                let Ok(body) = response.text().await else { return };

                LOGGER.info(format!("Connected to Strawberry API with IP {body}"));
            }
            else {
                LOGGER.error("Error while connecting to Strawberry API");
            }
        }
    }
}