# media_query/views.py

from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import cssutils

def count_media_queries(request):
    if request.method == 'POST':
        # Get the input URLs from the form
        urls = request.POST.get('urls', '').split('\n')

        results = []
        for url in urls:
            # Trim leading/trailing spaces and skip empty lines
            url = url.strip()
            if not url:
                continue

            try:
                # Make a request to the URL
                response = requests.get(url)
                response.raise_for_status()  # Raise exception for non-200 status codes

                # Parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find external CSS files
                external_css_urls = []
                link_tags = soup.find_all('link', {'rel': 'stylesheet'})
                for tag in link_tags:
                    href = tag.get('href')
                    if href and not href.startswith('data:') and not href.startswith('#'):
                        if not href.startswith('http'):
                            # Convert relative URLs to absolute URLs
                            href = f"{response.url.rstrip('/')}/{href.lstrip('/')}"
                        external_css_urls.append(href)

                # Find internal CSS media queries
                internal_media_queries_count = 0
                style_tags = soup.find_all('style')
                for tag in style_tags:
                    css = tag.string
                    if css:
                        parsed_css = cssutils.parseString(css)
                        for rule in parsed_css:
                            if rule.type == rule.MEDIA_RULE:
                                internal_media_queries_count += 1

                # Count media queries in external CSS files
                external_media_queries_count = 0
                for css_url in external_css_urls:
                    css_response = requests.get(css_url)
                    css_response.raise_for_status()
                    css_content = css_response.text
                    parsed_css = cssutils.parseString(css_content)
                    for rule in parsed_css:
                        if rule.type == rule.MEDIA_RULE:
                            external_media_queries_count += 1

                total_media_queries_count = internal_media_queries_count + external_media_queries_count

                results.append({'url': url, 'media_queries_count': total_media_queries_count})
            except (requests.RequestException, ValueError, TypeError) as e:
                results.append({'url': url, 'media_queries_count': f'Error: {str(e)}'})

        return render(request, 'media_query/results.html', {'results': results})

    return render(request, 'media_query/form.html')
