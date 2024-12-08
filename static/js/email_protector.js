// Protect email
const emailUsername = 'informaticapau';
const emailDomain = 'pm.me';

const openEmail = () => {
    document.getElementById('email').href = `mailto:${emailUsername}+fromweb@${emailDomain}`;
}
document.getElementById('email').setAttribute('onclick', 'openEmail();');