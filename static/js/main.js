/*=============== EXPANDED LIST ===============*/
const cnavExpand = document.getElementById('cnav-expand'),
    cnavExpandList = document.getElementById('cnav-expand-list'),
    cnavExpandIcon = document.getElementById('cnav-expand-icon')

cnavExpand.addEventListener('click', () => {
    // Expand list
    cnavExpandList.classList.toggle('show-list')

    // Rotate icon
    cnavExpandIcon.classList.toggle('rotate-icon')
})

/*=============== SCROLL SECTIONS ACTIVE LINK ===============*/
const sections = document.querySelectorAll('section[id]')

const pageActive = (path) => {
    sections.forEach(current => {
        const
            sectionId = current.getAttribute('id'),
            sectionsClass = document.querySelector('.cnav__list a[href*=' + sectionId + ']')
        if ('/page/'+current.id === path) {
            sectionsClass.classList.add('active-link')
        } else {
            sectionsClass.classList.remove('active-link')
        }
    })
}
//  window.addEventListener('scroll', scrollActive)

let path = location.pathname;
// console.log(path)
pageActive(path);