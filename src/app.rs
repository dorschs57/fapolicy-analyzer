use serde::Deserialize;
use serde::Serialize;

use crate::api::{Trust, TrustSource};
use crate::sys::Config;
use crate::trust::load_trust_db;
use crate::trust::Changeset;

/// Represents an immutable view of the application state.
/// Carries along the configuration that provided the state.
#[derive(Clone, Serialize, Deserialize)]
pub struct State {
    pub config: Config,
    pub trust_db: Vec<Trust>,
}

impl State {
    pub fn new(cfg: &Config) -> State {
        State {
            config: cfg.clone(),
            trust_db: load_trust_db(&cfg.trust_db_path),
        }
    }

    /// Apply a Changeset to this state, results in a new immutable state
    pub fn apply_trust_changes(&self, changes: Changeset) -> Self {
        println!("applying changeset to current state...");
        let updated_db = changes.apply(
            self.trust_db
                .iter()
                .filter(|t| t.source == TrustSource::Ancillary)
                .map(|t| (t.path.clone(), t.clone()))
                .collect(),
        );
        let updated_db = changes
            .apply(updated_db)
            .iter()
            .map(|e| e.1.clone())
            .collect();
        Self {
            config: self.config.clone(),
            trust_db: updated_db,
        }
    }
}