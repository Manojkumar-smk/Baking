function Footer() {
  return (
    <footer style={{
      backgroundColor: '#343a40',
      color: 'white',
      padding: '2rem 0',
      marginTop: 'auto'
    }}>
      <div className="container">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem' }}>
          <div>
            <h3 style={{ marginBottom: '1rem' }}>🍪 Cookie Shop</h3>
            <p style={{ color: '#adb5bd' }}>
              Fresh homemade cookies delivered to your door.
            </p>
          </div>

          <div>
            <h4 style={{ marginBottom: '1rem' }}>Quick Links</h4>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              <li><a href="/about" style={{ color: '#adb5bd' }}>About Us</a></li>
              <li><a href="/contact" style={{ color: '#adb5bd' }}>Contact</a></li>
              <li><a href="/terms" style={{ color: '#adb5bd' }}>Terms of Service</a></li>
              <li><a href="/privacy" style={{ color: '#adb5bd' }}>Privacy Policy</a></li>
            </ul>
          </div>

          <div>
            <h4 style={{ marginBottom: '1rem' }}>Contact Us</h4>
            <p style={{ color: '#adb5bd' }}>Email: info@cookieshop.com</p>
            <p style={{ color: '#adb5bd' }}>Phone: (555) 123-4567</p>
          </div>
        </div>

        <div style={{ borderTop: '1px solid #495057', marginTop: '2rem', paddingTop: '1rem', textAlign: 'center', color: '#6c757d' }}>
          <p>&copy; {new Date().getFullYear()} Cookie Shop. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
