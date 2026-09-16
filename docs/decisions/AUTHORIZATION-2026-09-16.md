# TI-0 execution authorization

- Author: Leonardo Maximino Bernardo
- Date: 2026-09-16
- Decision: approved
- Authorized phase: TI-0 only
- Blocked phases: TI-1 through TI-8
- Repository: `lmbernardo7520112/snbi-dendritic-fragmentation-ml`

## Authorized connection

GitHub access uses an OAuth or GitHub App integration. No password, personal
access token, private SSH key, recovery code, or two-factor code was shared with
the implementation agent. Repository access was confirmed by a read-only
metadata request before any write.

## Operational constraint

The authorization permits TI0-01 through TI0-09 only. Passing Gate G0 does not
authorize TI-1.

