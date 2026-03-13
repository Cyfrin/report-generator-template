TODO - Summary of the audit findings and any additional executive comments. Put in the finding numbers below, remove categories that don't apply (eg remove Critical from next sentence if no Crits found).

> The findings consist of X Critical, X High, X Medium & X Low severity issues with the remainder being informational and gas optimizations.

**Centralization Risks**

TODO - document any centralization risks here such as upgradeable contracts, admin features etc. Remove section if not required. Example text for TradFi protocol:

> The protocol by its regulated nature is highly centralized with protocol admins having complete power including the ability to upgrade many contracts to new implementations; protocol users must place complete trust in the protocol admins when engaging with the protocol. One benefit to this is that even if a serious bug should be discovered once the protocol is live, protocol admins will in many cases be able to upgrade the relevant contracts and resolve the issue.

**Protocol Invariants**

TODO - use fv-certora skill to generate & output invariants here OR remove Protocol Invariants section if it doesn't apply to your audit

**Post Audit Recommendations**

TODO - recommend a subsequent audit if significant risk still exists, can also recommend they write more test to cover a specific area of the protocol. Remove this secton if it isn't required. Some factors to consider:
- short audit? higher risk we missed something
- subtle crit/highs found late in the audit? higher risk we missed something
- simple crit/highs found early in the audit, then no more crit/highs? lower chance we missed something 

Some example texts:

> Although the codebase was small and the audit timeline short (5 working days), the protocol contained meaningful complexity. As significant vulnerabilities were identified (1 Critical, 1 High), we recommend an additional audit before deploying significant capital in a production environment.

> Due to the significant number of Critical and High severity findings it is statistically likely that more serious vulnerabilities still remain. While the current codebase is more robust and defensive from a security standpoint after mitigations, we recommend conducting an additional audit before deploying significant capital in a production environment.

> Considering the number of significant issues identified (3 Crit, 7 High), it is statistically likely that there are more complex bugs still present that could not be identified given the time-boxed nature of this engagement. Due to the number of issues significant identified, the non-trivial changes required during mitigation, and the short turnaround time for reviewing the mitigation fixes, it is recommended that a follow-up audit and development of a more complex stateful fuzz test suite be undertaken prior to deploying significant monetary capital to production.
