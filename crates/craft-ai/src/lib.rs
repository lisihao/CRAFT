//! CRAFT AI - Claude API integration
//!
//! This crate provides AI-powered capabilities:
//! - Claude API client
//! - Prompt engineering for code generation
//! - Rate limiting and error handling

use craft_core::{AiConfig, CraftError};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::time::Duration;
use tracing::{debug, info, warn};

/// Claude API client
pub struct ClaudeClient {
    /// HTTP client
    client: Client,
    /// API configuration
    config: AiConfig,
    /// API base URL
    base_url: String,
}

/// Message in Claude API format
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Message {
    pub role: String,
    pub content: String,
}

/// Claude API request
#[derive(Debug, Serialize)]
struct ClaudeRequest {
    model: String,
    max_tokens: u32,
    messages: Vec<Message>,
}

/// Claude API response
#[derive(Debug, Deserialize)]
struct ClaudeResponse {
    content: Vec<ContentBlock>,
}

#[derive(Debug, Deserialize)]
struct ContentBlock {
    text: String,
}

impl ClaudeClient {
    /// Create a new Claude client
    pub fn new(mut config: AiConfig) -> Result<Self, CraftError> {
        // Load API key from environment if not set
        if config.api_key.is_none() {
            config.api_key = std::env::var("ANTHROPIC_API_KEY").ok();
        }

        if config.api_key.is_none() {
            return Err(CraftError::Config(
                "ANTHROPIC_API_KEY not set".to_string(),
            ));
        }

        let client = Client::builder()
            .timeout(Duration::from_secs(120))
            .build()
            .map_err(|e| CraftError::AiApi(e.to_string()))?;

        Ok(Self {
            client,
            config,
            base_url: "https://api.anthropic.com/v1".to_string(),
        })
    }

    /// Send a message to Claude and get a response
    pub async fn send_message(&self, messages: Vec<Message>) -> Result<String, CraftError> {
        let request = ClaudeRequest {
            model: self.config.model.clone(),
            max_tokens: self.config.max_tokens,
            messages,
        };

        let api_key = self.config.api_key.as_ref().ok_or_else(|| {
            CraftError::Config("API key not configured".to_string())
        })?;

        let response = self
            .client
            .post(format!("{}/messages", self.base_url))
            .header("x-api-key", api_key)
            .header("anthropic-version", "2023-06-01")
            .header("content-type", "application/json")
            .json(&request)
            .send()
            .await
            .map_err(|e| CraftError::AiApi(e.to_string()))?;

        if !response.status().is_success() {
            let error_text = response.text().await.unwrap_or_default();
            return Err(CraftError::AiApi(format!(
                "API request failed: {}",
                error_text
            )));
        }

        let response: ClaudeResponse = response
            .json()
            .await
            .map_err(|e| CraftError::AiApi(e.to_string()))?;

        let text = response
            .content
            .first()
            .map(|c| c.text.clone())
            .unwrap_or_default();

        Ok(text)
    }

    /// Generate adapter code using AI
    pub async fn generate_adapter(
        &self,
        source_api: &str,
        target_api: &str,
        context: &str,
    ) -> Result<String, CraftError> {
        let prompt = format!(
            r#"You are an expert at generating adapter code for cross-platform API compatibility.

Source API (Android):
{source_api}

Target API (HarmonyOS):
{target_api}

Additional Context:
{context}

Generate a Java adapter class that:
1. Extends or implements the source API
2. Delegates calls to the target API
3. Handles any parameter or return type transformations
4. Includes proper error handling
5. Has clear documentation

Output only the Java code, no explanations."#
        );

        let messages = vec![Message {
            role: "user".to_string(),
            content: prompt,
        }];

        self.send_message(messages).await
    }

    /// Analyze API semantic similarity
    pub async fn analyze_similarity(
        &self,
        source_api: &str,
        target_api: &str,
    ) -> Result<f64, CraftError> {
        let prompt = format!(
            r#"Analyze the semantic similarity between these two APIs.

Source API:
{source_api}

Target API:
{target_api}

Rate the similarity from 0.0 to 1.0, where:
- 1.0 means identical functionality
- 0.8+ means direct mapping possible
- 0.5-0.8 means semantic mapping with transformation needed
- Below 0.5 means significant bridging required

Output only a single decimal number."#
        );

        let messages = vec![Message {
            role: "user".to_string(),
            content: prompt,
        }];

        let response = self.send_message(messages).await?;
        response
            .trim()
            .parse::<f64>()
            .map_err(|e| CraftError::AiApi(format!("Failed to parse similarity score: {}", e)))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_message_creation() {
        let msg = Message {
            role: "user".to_string(),
            content: "Hello".to_string(),
        };
        assert_eq!(msg.role, "user");
    }
}
