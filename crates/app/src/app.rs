/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use directories::ProjectDirs;
use serde::Deserialize;
use serde::Serialize;
use std::path::PathBuf;

use fapolicy_analyzer::users::{read_groups, read_users, Group, User};
use fapolicy_daemon::fapolicyd::Version;
use fapolicy_rules::db::DB as RulesDB;
use fapolicy_rules::ops::Changeset as RuleChanges;
use fapolicy_rules::read::load_rules_db;
use fapolicy_trust::db::DB as TrustDB;
use fapolicy_trust::ops::Changeset as TrustChanges;
use fapolicy_trust::{check, load};

use crate::cfg::All;
use crate::cfg::PROJECT_NAME;
use crate::error::Error;

/// Represents an immutable view of the application state.
/// Carries along the configuration that provided the state.
#[derive(Clone)]
pub struct State {
    pub config: All,
    pub trust_db: TrustDB,
    pub rules_db: RulesDB,
    pub users: Vec<User>,
    pub groups: Vec<Group>,
    pub daemon_version: Version,
}

impl State {
    pub fn empty(cfg: &All) -> State {
        State {
            config: cfg.clone(),
            trust_db: TrustDB::default(),
            rules_db: RulesDB::default(),
            users: vec![],
            groups: vec![],
            daemon_version: fapolicy_daemon::version(),
        }
    }

    pub fn load(cfg: &All) -> Result<State, Error> {
        let trust_db = load::trust_db(
            &PathBuf::from(&cfg.system.trust_lmdb_path),
            &PathBuf::from(&cfg.system.trust_dir_path),
            Some(&PathBuf::from(&cfg.system.trust_file_path)),
        )?;
        let rules_db = load_rules_db(&cfg.system.rules_file_path)?;
        Ok(State {
            config: cfg.clone(),
            trust_db,
            rules_db,
            users: read_users()?,
            groups: read_groups()?,
            daemon_version: fapolicy_daemon::version(),
        })
    }

    pub fn load_checked(cfg: &All) -> Result<State, Error> {
        let state = State::load(cfg)?;
        let trust_db = check::disk_sync(&state.trust_db)?;
        Ok(State { trust_db, ..state })
    }

    /// Apply a trust changeset to this state, results in a new immutable state
    pub fn apply_trust_changes(&self, changes: TrustChanges) -> Self {
        let modified = changes.apply(self.trust_db.clone());
        Self {
            config: self.config.clone(),
            trust_db: modified,
            rules_db: self.rules_db.clone(),
            users: self.users.clone(),
            groups: self.groups.clone(),
            daemon_version: self.daemon_version.clone(),
        }
    }

    /// Apply a rule changeset to this state, results in a new immutable state
    pub fn apply_rule_changes(&self, changes: RuleChanges) -> Self {
        let modified = changes.apply();
        Self {
            config: self.config.clone(),
            trust_db: self.trust_db.clone(),
            rules_db: modified.clone(),
            users: self.users.clone(),
            groups: self.groups.clone(),
            daemon_version: self.daemon_version.clone(),
        }
    }
}

#[derive(Clone, Serialize, Deserialize)]
pub struct Config {
    #[serde(default = "data_dir")]
    pub data_dir: String,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            data_dir: data_dir(),
        }
    }
}

//
// private helpers for serde
//

fn data_dir() -> String {
    let proj_dirs = ProjectDirs::from("rs", "", PROJECT_NAME).expect("failed to init project dirs");
    let dd = proj_dirs.data_dir();
    dd.to_path_buf().into_os_string().into_string().unwrap()
}
