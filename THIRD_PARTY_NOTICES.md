# Third-Party Notices

## AnalogGaugeWidgetPyQt
- Upstream: https://github.com/StefanHol/AnalogGaugeWidgetPyQt
- Intended local vendor module: `src/ui/third_party/analoggaugewidget/analoggaugewidget.py`
- License: Apache-2.0 (`src/ui/third_party/analoggaugewidget/LICENSE`)
- Notes:
  - This dependency is vendorized for the CLUSTER speed gauge integration.
  - The project uses a local PyQt6-compatible vendor copy, wrapped by `src/ui/components/speed_gauge_oem.py`.
  - Upstream direct fetch is blocked in this environment (HTTP 403), so synchronization must be done from a networked environment when needed.
