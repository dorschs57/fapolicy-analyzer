use crate::sys;
use thiserror::Error;

/// An Error that can occur in this crate
#[derive(Error, Debug)]
pub enum Error {
    #[error("System error: {0}")]
    SystemError(#[from] sys::Error),
    #[error("Trust error: {0}")]
    TrustError(#[from] fapolicy_trust::error::Error),
}