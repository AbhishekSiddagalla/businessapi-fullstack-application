export default function SendMessage() {
  return (
    <>
      <form>
        <h1>Send Message</h1>
        <label>from:</label> &nbsp;
        <input type="text" />
        <br />
        <br />
        <label>Template Name:</label> &nbsp;
        <input type="text" />
        <br />
        <br />
        <label>Parameter values:</label> &nbsp;
        <input type="text" />
        <br />
        <br />
        <label>To Numbers:</label> &nbsp;
        <input type="text" />
        <br />
        <br />
        <button>cancel</button> &nbsp;
        <button>Send</button>
      </form>
    </>
  );
}
