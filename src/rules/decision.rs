use crate::rules::parse;
use std::fmt::{Display, Formatter};
use std::str::FromStr;

/// # Decision
/// If the rule triggers, this is the access decision that fapolicyd will tell the kernel.
/// If the decision is one of the audit variety, then the decision will trigger a FANOTIFY audit event with all relevant information.
/// You must have at least one audit rule loaded to generate an audit event.
/// If the decision is one of the syslog variety, then the decision will trigger writing an event into syslog.
/// If the decision is of one the log variety, then it will create an audit event and a syslog event.
///
/// Regardless of the notification, any rule with a deny in the keyword will deny access and any with an allow in the keyword will allow access.
///
#[derive(Clone, Debug, PartialEq)]
pub enum Decision {
    AllowAudit,
    AllowSyslog,
    AllowLog,
    Allow,
    Deny,
    DenyLog,
    DenyAudit,
    DenySyslog,
}

impl Display for Decision {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Decision::Allow => f.write_str("allow"),
            Decision::Deny => f.write_str("deny"),
            Decision::DenyAudit => f.write_str("deny_audit"),
            Decision::AllowAudit => f.write_str("allow_audit"),
            Decision::AllowSyslog => f.write_str("allow_syslog"),
            Decision::AllowLog => f.write_str("allow_log"),
            Decision::DenyLog => f.write_str("deny_log"),
            Decision::DenySyslog => f.write_str("deny_syslog"),
        }
    }
}

impl FromStr for Decision {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match parse::decision(s) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Decision from string".into()),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn display() {
        assert_eq!(format!("{}", Decision::Allow), "allow");
        assert_eq!(format!("{}", Decision::Deny), "deny");
        assert_eq!(format!("{}", Decision::DenyAudit), "deny_audit");
    }
}