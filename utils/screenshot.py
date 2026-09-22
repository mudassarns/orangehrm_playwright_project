import base64

from pytest_html import extras


def capture_failure_screenshot(page):
    url = page.url

    page.evaluate(
        """(url) => {
            const banner = document.createElement('div');
            banner.id = 'failure-url-banner';
            banner.textContent = `URL: ${url}`;
            banner.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: 60px;
                background: white;
                color: black;
                font: 22px Arial, sans-serif;
                padding: 15px 10px;
                box-sizing: border-box;
                z-index: 2147483647;
            `;
            document.body.prepend(banner);
        }""",
        url,
    )

    screenshot_bytes = page.screenshot(full_page=True)

    page.evaluate(
        """() => {
            document.getElementById('failure-url-banner')?.remove();
        }"""
    )

    return screenshot_bytes


def attach_failure_screenshot(report, page):
    screenshot_bytes = capture_failure_screenshot(page)

    screenshot_base64 = base64.b64encode(
        screenshot_bytes
    ).decode("utf-8")

    report_extras = getattr(report, "extras", [])

    report_extras.append(
        extras.image(
            screenshot_base64,
            mime_type="image/png",
            name="Failure Screenshot",
        )
    )

    report.extras = report_extras
