export default function Icon({name='plus', size=20}) {
 const paths = {
 plus: 'M12 5v14M5 12h14', chat:'M21 11.5a8.5 8.5 0 0 1-8.5 8.5H4l-2 2V11.5A8.5 8.5 0 0 1 10.5 3h2a8.5 8.5 0 0 1 8.5 8.5Z',
 arrow:'m5 12 14 0m-6-6 6 6-6 6',check:'m5 12 4 4L19 6',clock:'M12 8v4l3 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0',
 calendar:'M5 5h14v16H5zM8 3v4m8-4v4M5 10h14',shield:'m12 3 8 4v5c0 5-8 9-8 9s-8-4-8-9V7l8-4Z',send:'m3 3 18 9-18 9 3-9-3-9Zm3 9h15',heart:'M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z'};
 return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={paths[name] || paths.plus}/></svg>;
}
