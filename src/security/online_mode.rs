use reqwest::Client;
use crate::global::{API, RUNTIME_LOGGER};


#[derive(Default)]
pub struct OnlineMode {
    pub enabled: bool,
    pub server_uuid: String,
    pub server_ip: String,
}

impl OnlineMode {
    pub fn new(enabled: bool) -> Self {
        Self {
            enabled,
            ..Default::default()
        }
    }

    pub async fn auth(&self) {
        if self.enabled {
            let client = Client::new();

            let Ok(response) = client.get(format!("{API}utils/user/ip")).send().await else {
                RUNTIME_LOGGER.warning("Could not send request to Strawberry API");
                return
            };

            if response.status().is_success() {
                let Ok(body) = response.text().await else { return };
                let json: serde_json::Value = serde_json::from_str(body.as_str()).unwrap();

                RUNTIME_LOGGER.info(format!("Connected to Strawberry API with IP {}", json["ip"].as_str().unwrap()));
            }
            else {
                RUNTIME_LOGGER.warning("Error while connecting to Strawberry API");
            }
        }
        else {
            RUNTIME_LOGGER.warning("Online Mode is disabled");
        }
    }
}