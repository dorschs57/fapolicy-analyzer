use std::time::SystemTime;

use pyo3::prelude::*;
use pyo3::{exceptions, PyResult};

use fapolicy_analyzer::events::db::DB as EventDB;
use fapolicy_analyzer::events::event::Event;
use fapolicy_app::app::State;
use fapolicy_app::cfg;
use fapolicy_app::sys::deploy_app_state;

use crate::acl::{PyGroup, PyUser};
use crate::analysis::PyEventLog;
use crate::change::PyChangeset;

use super::trust::PyTrust;

#[pyclass(module = "app", name = "System")]
#[derive(Clone)]
/// An immutable view of host system state.
/// This only a container for state, it has to be applied to the host system.
pub struct PySystem {
    rs: State,
}
impl From<State> for PySystem {
    fn from(rs: State) -> Self {
        Self { rs }
    }
}
impl From<PySystem> for State {
    fn from(py: PySystem) -> Self {
        py.rs
    }
}

#[pymethods]
impl PySystem {
    /// Create a new initialized System
    /// This returns a result object that will be an error if initialization fails,
    /// allowing the member accessors on the System to return non-result objects.
    #[new]
    fn new(py: Python) -> PyResult<PySystem> {
        py.allow_threads(|| {
            let conf = cfg::All::load()
                .map_err(|e| exceptions::PyRuntimeError::new_err(format!("{:?}", e)))?;
            let t = SystemTime::now();
            match State::load_checked(&conf) {
                Ok(state) => {
                    let d = t.elapsed().unwrap().as_secs();
                    println!("loaded system in {} seconds", d);
                    Ok(state.into())
                }
                Err(e) => Err(exceptions::PyRuntimeError::new_err(format!("{:?}", e))),
            }
        })
    }

    /// Obtain a list of trusted files sourced from the system trust database.
    /// The system trust is generated from the contents of the RPM database.
    /// This represents state in the current fapolicyd database, not necessarily
    /// matching what is currently in the RPM database.
    fn system_trust(&self) -> Vec<PyTrust> {
        self.rs
            .trust_db
            .values()
            .iter()
            .filter(|r| r.is_system())
            .map(|r| r.status.clone())
            .flatten()
            .map(PyTrust::from)
            .collect()
    }

    /// Obtain a list of trusted files sourced from the ancillary trust database.
    /// This represents state in the current fapolicyd database, not necessarily
    /// matching what is currently in the ancillary trust file.
    fn ancillary_trust(&self) -> Vec<PyTrust> {
        self.rs
            .trust_db
            .values()
            .iter()
            .filter(|r| r.is_ancillary())
            .map(|r| r.status.clone())
            .flatten()
            .map(PyTrust::from)
            .collect()
    }

    /// Apply the changeset to the state of this System generating a new System
    fn apply_changeset(&self, change: PyChangeset) -> PySystem {
        self.rs.apply_trust_changes(change.into()).into()
    }

    /// Update the host system with this state of this System
    fn deploy(&self) -> PyResult<()> {
        match deploy_app_state(&self.rs) {
            Ok(_) => Ok(()),
            Err(e) => Err(exceptions::PyRuntimeError::new_err(format!("{:?}", e))),
        }
    }

    /// Check the host system state against the state of this System
    fn is_stale(&self) -> bool {
        // todo;; check current state againt rpm and file
        false
    }

    /// Load a list of system users
    fn users(&self) -> Vec<PyUser> {
        self.rs.users.iter().map(|u| u.clone().into()).collect()
    }

    /// Load a list of system groups
    fn groups(&self) -> Vec<PyGroup> {
        self.rs.groups.iter().map(|g| g.clone().into()).collect()
    }

    /// Parse an EventLog from the specified path
    fn events(&self, log: &str) -> PyEventLog {
        let xs = Event::from_file(log);
        PyEventLog {
            rs: EventDB::from(xs),
            rs_trust: self.rs.trust_db.clone(),
        }
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PySystem>()?;
    Ok(())
}