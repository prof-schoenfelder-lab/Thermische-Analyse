document.addEventListener('DOMContentLoaded', function(){
  try{
    // find the sidebar TOC list
    const toc = document.querySelector('.md-nav--secondary .md-nav__list');
    if(!toc) return;
    // find all links inside the toc
    const links = Array.from(toc.querySelectorAll('a.md-nav__link'));
    if(links.length === 0) return;
    // find the current page link by comparing hrefs
    const currentHref = location.pathname.replace(/\/index.html$/, '/').replace(/^\./, '');
    // fallback: try to match by pathname end
    let currentIndex = links.findIndex(a => {
      const href = a.getAttribute('href');
      return href && (href === location.pathname || href === location.pathname.replace(/^(\.)?\//,'') || href.endsWith(location.pathname.split('/').pop()) || location.pathname.endsWith(href));
    });
    if(currentIndex === -1){
      // try matching against anchorless hrefs
      currentIndex = links.findIndex(a => location.pathname.endsWith(a.getAttribute('href')));
    }
    if(currentIndex === -1) return;

    const prevLink = links[currentIndex - 1];
    const nextLink = links[currentIndex + 1];
    if(!prevLink && !nextLink) return;

    const wrapper = document.createElement('div');
    wrapper.className = 'page-nav-wrapper';

    function makeBox(link, kind){
      const box = document.createElement(link? 'a' : 'div');
      box.className = 'page-nav ' + (kind === 'prev' ? 'page-nav--prev' : 'page-nav--next');
      if(link){
        box.href = link.getAttribute('href');
      } else {
        box.setAttribute('aria-hidden','true');
      }
      const label = document.createElement('div'); label.className = 'label'; label.textContent = (kind==='prev'?'Vorherige':'Nächste');
      const title = document.createElement('div'); title.className = 'title'; title.textContent = link? (link.textContent.trim()||link.getAttribute('href')) : '';
      box.appendChild(label); box.appendChild(title);
      return box;
    }

    const prevBox = makeBox(prevLink,'prev');
    const nextBox = makeBox(nextLink,'next');
    wrapper.appendChild(prevBox);
    wrapper.appendChild(nextBox);

    // insert after article content
    const article = document.querySelector('.md-content .md-content__inner');
    if(article){
      article.parentNode.insertBefore(wrapper, article.nextSibling);
    }
  }catch(e){console.error('page-nav-inject error', e)}
});
